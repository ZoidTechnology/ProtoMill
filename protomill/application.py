from asyncio import create_task, to_thread
from asyncio.exceptions import CancelledError
from collections.abc import Coroutine
from logging import getLogger
from typing import Any

from kipy import KiCad
from kipy.errors import ApiError, ConnectionError
from serial import Serial, SerialException
from serial.tools.list_ports import comports

from protomill.cam.design import Design, DesignError
from protomill.cam.layout import Layout
from protomill.cam.slots import Slots
from protomill.cnc.gcode import dwell, rapid_move, start_spindle, stop_spindle
from protomill.cnc.grbl.controller import GrblController
from protomill.cnc.routines import stream, wait_probe
from protomill.correction.fixture import FixtureCorrection
from protomill.correction.substrate import SubstrateCorrection
from protomill.errors import UserError
from protomill.geometry import Vector2D
from protomill.paths import settings_path
from protomill.settings import Optimization, Settings
from protomill.substrate.geometry import UNIT, Side, flip
from protomill.substrate.naming import size_suffix
from protomill.ui.page import Page
from protomill.ui.pages.busy import BusyPage
from protomill.ui.pages.connection import ConnectionPage
from protomill.ui.pages.design import DesignPage
from protomill.ui.pages.instruction import InstructionPage
from protomill.ui.pages.milling import MillingPage
from protomill.ui.pages.result import ResultPage, ResultStatus
from protomill.ui.pages.tool import ToolPage
from protomill.ui.step import StepStatus
from protomill.ui.window import Window


_STEPS = [
    "Import design",
    "Configure machine",
    "Prepare front side",
    "Mill front side",
    "Prepare back side",
    "Mill back side",
]

_MAX_BLOCK = {
    Optimization.NONE: 0,
    Optimization.LOW: 2,
    Optimization.MEDIUM: 4,
    Optimization.HIGH: 8,
}

_logger = getLogger(__name__)


class Application:
    def __init__(self) -> None:
        self._settings = Settings.load(settings_path())
        self._step = 0
        self._design_page = DesignPage(self._settings.design)
        self._window = Window(_STEPS, self._design_page, self.exit, self.exit)
        self._exiting = False
        self._error = None
        self._task = None
        self._port = None
        self._controller = None

    async def run(self) -> None:
        try:
            while not self._exiting:
                await self._run_task(self._process())

                if self._controller is not None:
                    if self._error is not None:
                        _logger.info("Resetting controller")

                        try:
                            self._controller.reset()
                        except Exception:
                            _logger.exception("Failed to reset controller")

                    _logger.info("Ensuring controller is stopped")
                    await self._controller.stop()
                    self._controller = None

                if self._port is not None:
                    _logger.info("Flushing serial port buffer")

                    try:
                        await to_thread(self._port.flush)
                    except Exception:
                        _logger.exception("Failed to flush serial port buffer")

                    _logger.info("Closing serial port")

                    try:
                        await to_thread(self._port.close)
                    except Exception:
                        _logger.exception("Failed to close serial port")

                    self._port = None

                if self._exiting:
                    break

                if self._error is not None:
                    step_status = StepStatus.ERROR
                    result_status = ResultStatus.ERROR

                    if isinstance(self._error, CancelledError):
                        title = "Cancelled"
                        message = "The process has been cancelled."
                    else:
                        title = "Error"

                        if isinstance(self._error, UserError):
                            message = str(self._error)
                        else:
                            message = "An unexpected error occurred. See the log for details."
                else:
                    step_status = StepStatus.SUCCESS
                    result_status = ResultStatus.SUCCESS
                    title = "Success"
                    message = "Milling is complete. The substrate is ready to use."

                self._window.on_secondary = self.exit
                self._window.update_step(self._step, step_status)
                await self._run_task(self._wait_page(ResultPage(result_status, title, message)))
        finally:
            await self._window.close()

    def exit(self) -> None:
        self._exiting = True
        self._cancel_task()

    async def _run_task(self, coroutine: Coroutine[Any, Any, None]) -> None:
        self._error = None
        self._task = create_task(coroutine)

        try:
            await self._task
        except BaseException as error:  # noqa: BLE001
            self._on_error(error)

        if self._error is None:
            _logger.info("Task completed")
            return

        if isinstance(self._error, CancelledError):  # pyright: ignore[reportUnnecessaryIsInstance]
            _logger.info("Task cancelled")
        else:
            _logger.error("Task failed", exc_info=self._error)

    def _cancel_task(self) -> None:
        if self._task is not None:
            self._task.cancel()

    def _on_error(self, error: BaseException) -> None:
        if self._error is None:
            self._error = error

    def _on_controller_error(self, error: Exception) -> None:
        self._on_error(error)
        self._cancel_task()

    async def _process(self) -> None:
        self._update_step(True)
        await self._wait_page(self._design_page)

        self._window.on_secondary = self._cancel_task
        self._window.update_page(BusyPage("Importing design..."))

        self._settings.design = self._design_page.read()
        await self._save_settings()

        design = await to_thread(self._import_design)

        cuts = design.cuts()
        slots = cuts.slots(self._settings.design.slot_length)

        tl, tr, bl, br = design.substrate_geometry.mounts
        mounts = {Side.FRONT: (bl, tl, tr, br), Side.BACK: (tl, bl, br, tr)}

        substrate_offset = FixtureCorrection.SUBSTRATE_OFFSET
        park_offset = Vector2D(-substrate_offset.x, substrate_offset.y) / UNIT

        optimized_slots: dict[Side, Slots] = {}

        for side in Side:
            start = mounts[side][-1].scale(1)
            end = flip(park_offset, side)
            ordered_slots = await slots[side].ordered(start)
            optimized_slots[side] = await ordered_slots.optimized(
                start, end, max_block=_MAX_BLOCK[self._settings.design.optimization]
            )

        ports = [port.device for port in await to_thread(comports)]

        if not ports:
            raise UserError("No serial ports found.")

        self._update_step()
        page = ConnectionPage(["Grbl"], ports, self._settings.connection)
        await self._wait_page(page)

        self._window.update_page(BusyPage("Connecting to CNC machine..."))

        self._settings.connection = page.read()
        await self._save_settings()

        try:
            self._port = await to_thread(
                Serial,
                self._settings.connection.port,
                self._settings.connection.baud_rate,
                timeout=0,
                write_timeout=0,
            )
        except SerialException as error:
            raise UserError("Failed to open serial port.") from error

        self._controller = GrblController(self._port, self._on_controller_error)
        await self._controller.initialize()

        page = MillingPage(self._settings.milling)
        await self._wait_page(page)

        self._settings.milling = page.read()
        await self._save_settings()

        fixture_correction = None

        for side in Side:
            self._update_step()

            if not optimized_slots[side].slots:
                self._update_step()
                continue

            if fixture_correction is None:
                await self._wait_page(
                    InstructionPage(
                        "fixture-feature",
                        "Position tool over fixture feature",
                        "Position the tool over the center of the <b>top-left fixture feature</b>, with the tool tip approximately 10 mm above the surface.",
                    )
                )

            suffix = size_suffix(flip(design.substrate_geometry.size, side))

            await self._wait_page(
                InstructionPage(
                    f"substrate-{suffix}",
                    f"Install substrate {"front" if side is Side.FRONT else "back"} side up",
                    f"Install the <b>substrate</b> into the fixture with the square mounting pad in the top-left corner. Ensure the silkscreen outline around the pad faces {"up" if side is Side.FRONT else "down"}.",
                )
            )

            self._window.update_page(
                InstructionPage(
                    f"substrate-mounts-{suffix}",
                    "Touch clip to mounting pad",
                    "Touch the clip to one of the substrate's <b>mounting pads</b>. The process will continue once contact is detected.",
                    False,
                )
            )

            status = await wait_probe(self._controller)

            await self._wait_page(
                ToolPage(
                    False,
                    "Attach clip to tool",
                    "Attach the <b>clip</b> so that it makes electrical contact with the <b>tool</b>. Ensure the clip stays attached during the probing sequence.",
                )
            )

            page = BusyPage("Probing fixture...")
            self._window.update_page(page)

            if fixture_correction is None:
                fixture_correction = FixtureCorrection()
                await fixture_correction.probe(status.position, self._controller)

            page.title = "Probing substrate..."  # pyright: ignore[reportAttributeAccessIssue]

            substrate_correction = SubstrateCorrection()
            await substrate_correction.probe(
                design.substrate_geometry.size,
                mounts[side],
                side,
                fixture_correction,
                self._controller,
            )

            await self._wait_page(
                ToolPage(
                    True,
                    "Remove clip from tool",
                    "Remove the <b>clip</b> from the <b>tool</b>. Ensure the clip and its wire are clear of the substrate.",
                )
            )

            self._update_step()
            page = BusyPage(f"Milling {"front" if side is Side.FRONT else "back"} side...", True)
            self._window.update_page(page)

            lines, physical = optimized_slots[side].gcode(
                substrate_correction, self._settings.milling
            )

            start_lines = [start_spindle(self._settings.milling.spindle_speed)]

            if self._settings.milling.spindle_acceleration_time != 0:
                start_lines.append(dwell(self._settings.milling.spindle_acceleration_time))

            ideal = fixture_correction.apply_inverse(physical)
            travel_height = fixture_correction.apply(ideal).z + fixture_correction.TRAVEL_HEIGHT
            park_position = fixture_correction.apply(Vector2D(0, 0))

            end_lines = [
                rapid_move(z=travel_height),
                rapid_move(
                    park_position.x,
                    park_position.y,
                    park_position.z + fixture_correction.TRAVEL_HEIGHT,
                ),
                stop_spindle(),
            ]

            await stream(
                self._controller,
                start_lines + lines + end_lines,
                status.buffer,
                lambda progress: setattr(page, "progress", progress),  # noqa: B023
            )

    def _update_step(self, reset: bool = False) -> None:
        self._step = 0 if reset else self._step + 1
        self._window.update_step(self._step, StepStatus.ACTIVE)

    async def _wait_page(self, page: Page) -> None:
        self._window.update_page(page)
        await self._window.primary()

    async def _save_settings(self) -> None:
        await to_thread(self._settings.save, settings_path())

    def _import_design(self) -> Layout:
        try:
            kicad = KiCad()
            version = kicad.get_version()

            if version.major < 10:
                raise UserError(
                    f"KiCad {version.full_version} is not supported. KiCad 10 or later is required."
                )

            board = kicad.get_board()
            design = Design(board)

            try:
                layout = design.layout(self._settings.design.tolerance)
            except DesignError as error:
                design.update_markers(error.violations)
                raise

            design.update_markers([])
            return layout
        except ConnectionError as error:
            raise UserError(
                "Failed to connect to KiCad. Ensure KiCad is running and the API is enabled."
            ) from error
        except ApiError as error:
            raise UserError(
                "Failed to import the design from KiCad. Ensure the project's PCB is open and no tool or dialog is active."
            ) from error
