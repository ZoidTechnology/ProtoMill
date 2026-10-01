from PySide6.QtCore import Property

from protomill.ui.page import TextPage


class InstructionPage(TextPage):
    def __init__(self, image: str, title: str, body: str, primary_enabled: bool = True) -> None:
        super().__init__("Instruction", title, body, primary_enabled)
        self._image = image

    @Property(str, constant=True)
    def image(self) -> str:
        return self._image
