from PySide6.QtCore import Property

from protomill.ui.page import TextPage


class ToolPage(TextPage):
    def __init__(self, reverse: bool, title: str, body: str) -> None:
        super().__init__("Tool", title, body)
        self._reverse = reverse

    @Property(bool, constant=True)
    def reverse(self) -> bool:
        return self._reverse
