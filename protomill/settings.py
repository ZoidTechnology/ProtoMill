from dataclasses import asdict, dataclass, fields, is_dataclass, replace
from enum import Enum
from json import dumps, loads
from logging import getLogger
from pathlib import Path
from typing import Any, Self

from protomill.utility import escape_path, escape_string


_logger = getLogger(__name__)


class Optimization(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class DesignSettings:
    tolerance: float = 0.1
    slot_length: float = 1.0
    optimization: Optimization = Optimization.MEDIUM


@dataclass(frozen=True)
class ConnectionSettings:
    controller: str = ""
    port: str = ""
    baud_rate: int = 115200


@dataclass(frozen=True)
class MillingSettings:
    depth: float = 0.1
    passes: int = 1
    spindle_speed: float = 1000.0
    spindle_acceleration_time: float = 1.0
    plunge_rate: float = 50.0
    feed_rate: float = 100.0


@dataclass
class Settings:
    design: DesignSettings = DesignSettings()
    connection: ConnectionSettings = ConnectionSettings()
    milling: MillingSettings = MillingSettings()

    @classmethod
    def load(cls, path: Path) -> Self:
        _logger.info("Loading settings from %s", escape_path(path))

        try:
            value = loads(path.read_text())

            if type(value) is not dict:
                raise TypeError("Root is not a JSON object")

            return _merge(cls(), value)
        except Exception:
            _logger.exception("Failed to load settings")
            return cls()

    def save(self, path: Path) -> None:
        _logger.info("Saving settings to %s", escape_path(path))

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"{dumps(asdict(self), default=_encode, indent=4)}\n")
        except Exception:
            _logger.exception("Failed to save settings")


def _merge(default: Any, value: Any, name: str = "") -> Any:
    if is_dataclass(default) and not isinstance(default, type) and type(value) is dict:
        prefix = f"{name}." if name else ""

        values = {
            field.name: _merge(getattr(default, field.name), value[field.name], prefix + field.name)
            for field in fields(default)
            if field.name in value
        }

        return replace(default, **values)

    if isinstance(default, Enum):
        try:
            return type(default)(value)
        except ValueError:
            pass

    if type(default) is float and type(value) is int:
        return float(value)

    if type(default) is type(value):
        return value

    _logger.error("Invalid value %s for %s", escape_string(str(value)), name)
    return default


def _encode(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    raise TypeError(f"Cannot serialize {type(value).__name__}")
