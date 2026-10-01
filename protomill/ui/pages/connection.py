from PySide6.QtCore import Property

from protomill.settings import ConnectionSettings
from protomill.ui.input import ChoiceInput, IntInput
from protomill.ui.page import Page


class ConnectionPage(Page):
    def __init__(
        self, controllers: list[str], ports: list[str], settings: ConnectionSettings
    ) -> None:
        super().__init__("Connection")
        self._controller = ChoiceInput.from_values(controllers, settings.controller)
        self._port = ChoiceInput.from_values(ports, settings.port)
        self._baud_rate = IntInput(settings.baud_rate)

    @Property(ChoiceInput, constant=True)
    def controller(self) -> ChoiceInput[str]:
        return self._controller

    @Property(ChoiceInput, constant=True)
    def port(self) -> ChoiceInput[str]:
        return self._port

    @Property(IntInput, constant=True)
    def baudRate(self) -> IntInput:
        return self._baud_rate

    def read(self) -> ConnectionSettings:
        return ConnectionSettings(self._controller.value, self._port.value, self._baud_rate.value)
