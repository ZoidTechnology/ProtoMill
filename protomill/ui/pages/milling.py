from PySide6.QtCore import Property

from protomill.settings import MillingSettings
from protomill.ui.input import FloatInput, IntInput
from protomill.ui.page import Page


class MillingPage(Page):
    def __init__(self, settings: MillingSettings) -> None:
        super().__init__("Milling")
        self._depth = FloatInput(settings.depth)
        self._passes = IntInput(settings.passes)
        self._spindle_speed = FloatInput(settings.spindle_speed)
        self._spindle_acceleration_time = FloatInput(settings.spindle_acceleration_time)
        self._plunge_rate = FloatInput(settings.plunge_rate)
        self._feed_rate = FloatInput(settings.feed_rate)

    @Property(FloatInput, constant=True)
    def depth(self) -> FloatInput:
        return self._depth

    @Property(IntInput, constant=True)
    def passes(self) -> IntInput:
        return self._passes

    @Property(FloatInput, constant=True)
    def spindleSpeed(self) -> FloatInput:
        return self._spindle_speed

    @Property(FloatInput, constant=True)
    def spindleAccelerationTime(self) -> FloatInput:
        return self._spindle_acceleration_time

    @Property(FloatInput, constant=True)
    def plungeRate(self) -> FloatInput:
        return self._plunge_rate

    @Property(FloatInput, constant=True)
    def feedRate(self) -> FloatInput:
        return self._feed_rate

    def read(self) -> MillingSettings:
        return MillingSettings(
            self._depth.value,
            self._passes.value,
            self._spindle_speed.value,
            self._spindle_acceleration_time.value,
            self._plunge_rate.value,
            self._feed_rate.value,
        )
