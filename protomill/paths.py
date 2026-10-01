from functools import cache
from os import environ
from pathlib import Path
from sys import platform

from protomill.identity import NAME


def log_path() -> Path:
    if platform == "darwin":
        directory = _home_directory() / "Library" / "Logs" / NAME
    else:
        directory = _state_directory()

    return directory / "log.txt"


def resource_path(resource: str) -> Path:
    return _resources_directory() / resource


def settings_path() -> Path:
    return _state_directory() / "settings.json"


def _environment_directory(variable: str, default: Path) -> Path:
    value = environ.get(variable)

    if value:
        directory = Path(value)

        if directory.is_absolute():
            return directory

    return default


@cache
def _home_directory() -> Path:
    return Path.home()


@cache
def _resources_directory() -> Path:
    return Path(__file__).parents[1] / "resources"


@cache
def _state_directory() -> Path:
    home = _home_directory()

    if platform == "darwin":
        return home / "Library" / "Application Support" / NAME

    if platform == "win32":
        return _environment_directory("LOCALAPPDATA", home / "AppData" / "Local") / NAME

    return _environment_directory("XDG_STATE_HOME", home / ".local" / "state") / NAME.lower()
