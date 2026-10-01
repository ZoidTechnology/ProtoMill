from PySide6.QtCore import Property, Signal

from protomill.ui.page import TextPage


class BusyPage(TextPage):
    progressChanged = Signal()

    def __init__(self, title: str, determinate: bool = False) -> None:
        super().__init__("Busy", title, primary_enabled=False)
        self._determinate = determinate
        self._progress = 0

    @Property(bool, constant=True)
    def determinate(self) -> bool:
        return self._determinate

    @Property(float, notify=progressChanged)
    def progress(self) -> float:  # pyright: ignore[reportRedeclaration]
        return self._progress

    @progress.setter
    def progress(self, value: float) -> None:
        self._progress = value
        self.progressChanged.emit()
