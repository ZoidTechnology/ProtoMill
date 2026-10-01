from collections.abc import Sequence
from dataclasses import dataclass

from PySide6.QtCore import Property, QObject

from protomill.utility import format_decimal


class _NumberInput(QObject):
    def __init__(self, real: bool, text: str) -> None:
        super().__init__()
        self._real = real
        self._text = text

    @Property(bool, constant=True)
    def real(self) -> bool:
        return self._real

    @Property(str)
    def text(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value


class IntInput(_NumberInput):
    def __init__(self, value: int) -> None:
        super().__init__(False, str(value))

    @property
    def value(self) -> int:
        return int(self._text)


class FloatInput(_NumberInput):
    def __init__(self, value: float) -> None:
        super().__init__(True, format_decimal(value))

    @property
    def value(self) -> float:
        return float(self._text)


@dataclass(frozen=True)
class Option[T]:
    label: str
    value: T


class ChoiceInput[T](QObject):
    def __init__(self, options: Sequence[Option[T]], value: T) -> None:
        super().__init__()
        self._options = options
        self._index = next(
            (index for index, option in enumerate(self._options) if option.value == value), 0
        )

    @staticmethod
    def from_values[U](values: Sequence[U], value: U) -> ChoiceInput[U]:
        return ChoiceInput([Option(str(item), item) for item in values], value)

    @Property(list, constant=True)
    def labels(self) -> list[str]:
        return [option.label for option in self._options]

    @Property(int)
    def index(self) -> int:  # pyright: ignore[reportRedeclaration]
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        self._index = index

    @property
    def value(self) -> T:
        return self._options[self._index].value
