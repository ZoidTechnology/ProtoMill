from asyncio import Event
from collections.abc import Callable

from PySide6.QtQml import QQmlApplicationEngine

from protomill.identity import NAME, VERSION
from protomill.paths import resource_path
from protomill.ui.page import Page
from protomill.ui.step import Step, StepStatus


class Window:
    def __init__(
        self,
        steps: list[str],
        page: Page,
        on_secondary: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self._engine = QQmlApplicationEngine()
        self._step = Step(0, StepStatus.ACTIVE)
        self._page = page
        self._primary_event = Event()
        self.on_secondary = on_secondary
        self.on_exit = on_exit

        self._engine.setInitialProperties(
            {"name": NAME, "version": VERSION, "steps": steps, "step": self._step, "page": page}
        )
        self._engine.load(resource_path("qml/Main.qml"))

        self._root = self._engine.rootObjects()[0]

        self._root.primary.connect(self._primary_event.set)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        self._root.secondary.connect(lambda: self.on_secondary())  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        self._root.exit.connect(lambda: self.on_exit())  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]

    def update_step(self, index: int, status: StepStatus) -> None:
        step = Step(index, status)
        self._root.setProperty("step", step)
        self._step = step

    def update_page(self, page: Page) -> None:
        if self._page is page:
            return

        self._root.setProperty("page", page)
        self._page = page

    async def primary(self) -> None:
        self._primary_event.clear()
        await self._primary_event.wait()

    async def close(self) -> None:
        closed = Event()
        self._root.destroyed.connect(closed.set)
        self._root.deleteLater()
        await closed.wait()
