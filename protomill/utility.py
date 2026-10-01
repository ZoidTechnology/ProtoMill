from pathlib import Path


def chain_error[T: BaseException](error: T, cause: BaseException) -> T:
    error.__cause__ = cause
    return error


def escape_path(path: Path) -> str:
    return escape_string(path.as_posix())


def escape_string(string: str) -> str:
    escaped = repr(string)

    if escaped.startswith('"'):
        return escaped

    return f'"{escaped[1:-1].replace("\\'", "'").replace('"', '\\"')}"'


def format_decimal(value: float, max_places: int = 3) -> str:
    return f"{value:z.{max_places}f}".rstrip("0").rstrip(".")
