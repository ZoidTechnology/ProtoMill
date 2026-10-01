from asyncio import Future, get_running_loop, shield
from collections.abc import Callable, Generator
from contextlib import contextmanager
from logging import getLogger

from serial import Serial

from protomill.cnc.controller import Controller, StatusResponse
from protomill.cnc.grbl.parser import (
    AlarmMessage,
    ErrorMessage,
    Message,
    OkMessage,
    ProbeMessage,
    StatusMessage,
    WelcomeMessage,
    parse_message,
    parse_position,
)
from protomill.errors import UserError
from protomill.geometry import Vector3D
from protomill.utility import escape_string


_logger = getLogger(__name__)


class GrblController(Controller):
    def __init__(self, port: Serial, on_error: Callable[[Exception], object]) -> None:
        super().__init__(port, on_error)
        self._pending: Future[None] = get_running_loop().create_future()
        self._pending.set_result(None)
        self._subscribers: dict[type[Message], set[Future[Message]]] = {}

    async def initialize(self) -> None:
        with self._subscribe(WelcomeMessage) as future:
            self.reset()
            response = await future

        if not response.version.startswith("1.1"):
            raise UserError(
                f"Grbl {response.version} is not supported. Grbl 1.1 or later is required."
            )

        await self.send("$X")
        await self.send("$10=3")

    async def status(self) -> StatusResponse:
        with self._subscribe(StatusMessage) as future:
            self._write("?")
            response = await future

        idle = response.state == "Idle"
        position = parse_position(response.data["MPos"])
        probe = "P" in response.data.get("Pn", "")
        buffer_field = response.data.get("Bf")
        buffer = None if buffer_field is None else int(buffer_field.split(",")[0])

        return StatusResponse(idle, position, probe, buffer)

    async def send(self, line: str) -> None:
        if not self._pending.done():
            raise RuntimeError("A command is already in progress")

        self._write(f"{line}\n")
        self._pending = get_running_loop().create_future()
        await shield(self._pending)

    async def probe(self, line: str) -> Vector3D:
        with self._subscribe(ProbeMessage) as future:
            await self.send(line)

            if not future.done():
                raise UserError("Probe response was not received.")

        response = future.result()

        if not response.success:
            raise UserError("Probe failed.")

        return response.position

    def reset(self) -> None:
        self._write("\x18")

    async def stop(self) -> None:
        await super().stop()

        self._pending.cancel()

        for futures in self._subscribers.values():
            for future in futures:
                future.cancel()

    def _on_line(self, line: str) -> None:
        message = parse_message(line)

        if message is None:
            _logger.warning("Failed to parse %s", escape_string(line))
            return

        match message:
            case AlarmMessage():
                self._on_error(UserError(f"Grbl alarm {message.code}."))
            case ErrorMessage():
                if self._pending.done():
                    self._on_error(UserError("Received an unexpected error message."))
                else:
                    self._pending.set_exception(UserError(f"Grbl error {message.code}."))
            case OkMessage():
                if self._pending.done():
                    self._on_error(UserError("Received an unexpected OK message."))
                else:
                    self._pending.set_result(None)

        for future in self._subscribers.get(type(message), ()):
            if not future.done():
                future.set_result(message)

    def _on_poll_error(self, error: Exception) -> None:
        if not self._pending.done():
            self._pending.set_exception(error)

        for futures in self._subscribers.values():
            for future in futures:
                if not future.done():
                    future.set_exception(error)

        self._on_error(error)

    @contextmanager
    def _subscribe[T: Message](self, message_type: type[T]) -> Generator[Future[T]]:
        future = get_running_loop().create_future()
        futures = self._subscribers.setdefault(message_type, set())
        futures.add(future)

        try:
            yield future
        finally:
            futures.remove(future)

            if future.done() and not future.cancelled():
                future.exception()
