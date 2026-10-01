from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from protomill.geometry import Vector3D


class Message(ABC):
    @classmethod
    @abstractmethod
    def parse(cls, line: str) -> Self | None:
        pass


@dataclass(frozen=True)
class AlarmMessage(Message):
    code: int

    @classmethod
    def parse(cls, line: str) -> Self | None:
        if line.startswith("ALARM:"):
            return cls(int(line[6:]))


@dataclass(frozen=True)
class ErrorMessage(Message):
    code: int

    @classmethod
    def parse(cls, line: str) -> Self | None:
        if line.startswith("error:"):
            return cls(int(line[6:]))


@dataclass(frozen=True)
class OkMessage(Message):
    @classmethod
    def parse(cls, line: str) -> Self | None:
        if line == "ok":
            return cls()


@dataclass(frozen=True)
class ProbeMessage(Message):
    position: Vector3D
    success: bool

    @classmethod
    def parse(cls, line: str) -> Self | None:
        if line.startswith("[PRB:") and line.endswith("]"):
            position, success = line[5:-1].split(":")
            return cls(parse_position(position), success != "0")


@dataclass(frozen=True)
class StatusMessage(Message):
    state: str
    data: dict[str, str]

    @classmethod
    def parse(cls, line: str) -> Self | None:
        if line.startswith("<") and line.endswith(">"):
            state, *fields = line[1:-1].split("|")
            data = dict(field.split(":") for field in fields)
            return cls(state, data)


@dataclass(frozen=True)
class WelcomeMessage(Message):
    version: str

    @classmethod
    def parse(cls, line: str) -> Self | None:
        if line.startswith("Grbl ") and line.endswith(" ['$' for help]"):
            return cls(line[5:-15])


def parse_message(line: str) -> Message | None:
    for message_type in Message.__subclasses__():
        if message := message_type.parse(line):
            return message


def parse_position(position: str) -> Vector3D:
    return Vector3D(*map(float, position.split(",")))
