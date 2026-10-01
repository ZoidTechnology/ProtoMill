from dataclasses import dataclass
from enum import Enum
from typing import Self

from protomill.geometry import GridSegment2D, GridVector2D, Vector2D


UNIT = 2.54
SUBSTRATE_SIZES = frozenset({GridVector2D(20, 20), GridVector2D(40, 20), GridVector2D(40, 40)})


@dataclass(frozen=True)
class SubstrateGeometry:
    size: GridVector2D
    mounts: list[GridVector2D]
    pads: set[GridVector2D]
    tracks: set[GridSegment2D]
    mount_entries: set[GridSegment2D]
    mount_internals: set[GridSegment2D]

    @classmethod
    def from_size(cls, size: GridVector2D) -> Self:
        mounts: list[GridVector2D] = []
        pads = {GridVector2D(x, y) for x in range(1, size.x) for y in range(1, size.y)}
        mount_entries: set[GridSegment2D] = set()
        mount_internals: set[GridSegment2D] = set()

        for y, dy in (0, 1), (size.y, -1):
            for x, dx in (0, 1), (size.x, -1):
                mount = GridVector2D(x + dx * 2, y + dy * 2)
                mounts.append(mount)
                pads.difference_update((mount, *mount.neighbors()))

                mount_internals.update(
                    (
                        GridSegment2D(mount, mount + GridVector2D(dx, 0)),
                        GridSegment2D(mount, mount + GridVector2D(0, dy)),
                    )
                )

                mount_entries.update(
                    (
                        GridSegment2D(mount + GridVector2D(dx, 0), mount + GridVector2D(dx * 2, 0)),
                        GridSegment2D(mount + GridVector2D(0, dy), mount + GridVector2D(0, dy * 2)),
                    )
                )

        tracks = {
            GridSegment2D(pad, neighbor)
            for pad in pads
            for neighbor in pad.neighbors()
            if neighbor in pads
        }

        return cls(size, mounts, pads, tracks | mount_entries, mount_entries, mount_internals)


class Side(Enum):
    FRONT = 0
    BACK = 1

    @staticmethod
    def from_segment(segment: GridSegment2D) -> Side:
        match segment.displacement():
            case GridVector2D(0, 1) | GridVector2D(1, 1):
                return Side.FRONT
            case GridVector2D(1, 0) | GridVector2D(1, -1):
                return Side.BACK

        raise ValueError("Segment endpoints must be neighbors")


def flip[T: (Vector2D, GridVector2D)](position: T, side: Side) -> T:
    if side is Side.FRONT:
        return position

    if isinstance(position, Vector2D):
        return Vector2D(position.y, position.x)

    return GridVector2D(position.y, position.x)
