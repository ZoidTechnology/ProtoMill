from collections.abc import Sequence
from re import compile
from typing import Self

from kipy.board_types import BoardPolygon, FootprintInstance
from kipy.geometry import Box2
from kipy.proto.board.board_types_pb2 import BoardLayer
from kipy.wrapper import Wrapper

from protomill.substrate.naming import FOOTPRINT_PREFIX


_PATTERN = compile(rf"{FOOTPRINT_PREFIX}[1-9]x[1-9]")


class SubstrateFootprint:
    def __init__(self, footprint: FootprintInstance) -> None:
        self._footprint = footprint

    @classmethod
    def from_items(cls, items: Sequence[Wrapper]) -> list[Self]:
        return [
            cls(item)
            for item in items
            if isinstance(item, FootprintInstance)
            and _PATTERN.fullmatch(item.definition.id.name) is not None
        ]

    def bounds(self) -> Box2 | None:
        polygons = [
            shape
            for shape in self._footprint.definition.shapes
            if isinstance(shape, BoardPolygon) and shape.layer == BoardLayer.BL_Edge_Cuts
        ]

        if len(polygons) != 1:
            return None

        return polygons[0].bounding_box()

    def pads(self) -> set[str]:
        return {pad.id.value for pad in self._footprint.definition.pads}
