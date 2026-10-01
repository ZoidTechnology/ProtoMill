from enum import Enum

from PySide6.QtCore import Property

from protomill.ui.page import TextPage


class ResultStatus(Enum):
    SUCCESS = ""
    ERROR = "error"


class ResultPage(TextPage):
    def __init__(self, status: ResultStatus, title: str, body: str) -> None:
        super().__init__("Result", title, body, primary_text="Restart", secondary_text="Exit")
        self._status = status

    @Property(str, constant=True)
    def status(self) -> str:
        return self._status.value
