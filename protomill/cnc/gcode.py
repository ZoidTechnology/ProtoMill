from protomill.utility import format_decimal


def rapid_move(x: float | None = None, y: float | None = None, z: float | None = None) -> str:
    return _append_words("G0", x=x, y=y, z=z)


def linear_move(
    x: float | None = None,
    y: float | None = None,
    z: float | None = None,
    feed: float | None = None,
) -> str:
    return _append_words("G1", x=x, y=y, z=z, f=feed)


def dwell(time: float) -> str:
    return _append_words("G4", p=time)


def probe(
    x: float | None = None,
    y: float | None = None,
    z: float | None = None,
    feed: float | None = None,
) -> str:
    return _append_words("G38.3", x=x, y=y, z=z, f=feed)


def start_spindle(speed: float | None = None) -> str:
    return _append_words("M3", s=speed)


def stop_spindle() -> str:
    return "M5"


def _append_words(line: str, **words: float | None) -> str:
    for letter, value in words.items():
        if value is not None:
            line += f" {letter.upper()}{format_decimal(value)}"

    return line
