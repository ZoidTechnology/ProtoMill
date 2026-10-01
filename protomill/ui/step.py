from enum import Enum

from PySide6.QtCore import Property, QObject


class StepStatus(Enum):
    ACTIVE = ""
    SUCCESS = "success"
    ERROR = "error"


class Step(QObject):
    def __init__(self, index: int, status: StepStatus) -> None:
        super().__init__()
        self._index = index
        self._status = status

    @Property(int, constant=True)
    def index(self) -> int:
        return self._index

    @Property(str, constant=True)
    def status(self) -> str:
        return self._status.value
