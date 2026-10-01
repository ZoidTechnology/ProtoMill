from PySide6.QtCore import Property

from protomill.settings import DesignSettings, Optimization
from protomill.ui.input import ChoiceInput, FloatInput, Option
from protomill.ui.page import Page


_OPTIMIZATION_OPTIONS = (
    Option("None", Optimization.NONE),
    Option("Low", Optimization.LOW),
    Option("Medium", Optimization.MEDIUM),
    Option("High", Optimization.HIGH),
)


class DesignPage(Page):
    def __init__(self, settings: DesignSettings) -> None:
        super().__init__("Design", secondary_text="Exit")
        self._tolerance = FloatInput(settings.tolerance * 100)
        self._slot_length = FloatInput(settings.slot_length)
        self._optimization = ChoiceInput(_OPTIMIZATION_OPTIONS, settings.optimization)

    @Property(FloatInput, constant=True)
    def tolerance(self) -> FloatInput:
        return self._tolerance

    @Property(FloatInput, constant=True)
    def slotLength(self) -> FloatInput:
        return self._slot_length

    @Property(ChoiceInput, constant=True)
    def optimization(self) -> ChoiceInput[Optimization]:
        return self._optimization

    def read(self) -> DesignSettings:
        return DesignSettings(
            self._tolerance.value / 100, self._slot_length.value, self._optimization.value
        )
