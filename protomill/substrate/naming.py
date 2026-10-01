from protomill.geometry import GridVector2D
from protomill.identity import NAME


SYMBOL_NAME = f"{NAME}_Substrate"
FOOTPRINT_PREFIX = f"{SYMBOL_NAME}_"


def size_suffix(size: GridVector2D) -> str:
    size //= 10
    return f"{size.x}x{size.y}"
