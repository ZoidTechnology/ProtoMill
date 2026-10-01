from math import sqrt

from protomill.geometry import GridVector2D, Vector2D
from protomill.identity import NAME
from protomill.substrate.geometry import SUBSTRATE_SIZES, UNIT
from protomill.substrate.naming import FOOTPRINT_PREFIX, size_suffix
from protomill.utility import format_decimal
from tools.kicad import Attribute, Node, property_node, quote
from tools.utility import BUILD_DIRECTORY


_LIBRARY_DIRECTORY = BUILD_DIRECTORY / f"{NAME}.pretty"

_PAD_DIAMETER = 1.5
_MOUNT_INSET = 2 * UNIT
_MOUNT_SIZE = 2 * UNIT + _PAD_DIAMETER
_MOUNT_DRILL = 3.5
_SILK_CORNER_OFFSET = Vector2D(1.5, 1.5) * UNIT

_OUTLINE_STROKE = 0.05
_SILK_STROKE = 0.25


def _main() -> None:
    _LIBRARY_DIRECTORY.mkdir(parents=True, exist_ok=True)

    for size in SUBSTRATE_SIZES:
        name = f"{FOOTPRINT_PREFIX}{size_suffix(size)}"
        file = _LIBRARY_DIRECTORY / f"{name}.kicad_mod"
        file.write_text(_build_footprint(name, size))


def _build_footprint(name: str, size: GridVector2D) -> str:
    corner_offset = size.scale(UNIT / 2)
    top_left_mount = Vector2D(_MOUNT_INSET, _MOUNT_INSET) - corner_offset

    root = Node(
        "footprint",
        quote(name),
        Node("version", 20260206),
        Node("generator", quote(NAME.lower())),
        property_node("Reference", "Ref**", Node("hide", True)),
        property_node("Value", name, Node("hide", True)),
        _graphic_node(
            "fp_rect",
            "F.SilkS",
            _SILK_STROKE,
            _position_node("start", top_left_mount - _SILK_CORNER_OFFSET),
            _position_node("end", top_left_mount + _SILK_CORNER_OFFSET),
            Node("radius", UNIT / 2),
        ),
    )

    outline = Node("pts")

    for index, start_direction in enumerate(
        (Vector2D(-1, 0), Vector2D(0, -1), Vector2D(1, 0), Vector2D(0, 1))
    ):
        end_direction = Vector2D(-start_direction.y, start_direction.x)
        corner_direction = start_direction + end_direction
        radius = UNIT if index == 0 else _MOUNT_INSET

        center = Vector2D(
            corner_direction.x * (corner_offset.x - radius),
            corner_direction.y * (corner_offset.y - radius),
        )

        outline.append(
            Node(
                "arc",
                _position_node("start", center + start_direction * radius),
                _position_node("mid", center + corner_direction * radius / sqrt(2)),
                _position_node("end", center + end_direction * radius),
            )
        )

    root.append(_graphic_node("fp_poly", "Edge.Cuts", _OUTLINE_STROKE, outline))

    for number, position in enumerate(
        (
            Vector2D(x, y)
            for y in (top_left_mount.y, -top_left_mount.y)
            for x in (top_left_mount.x, -top_left_mount.x)
        ),
        1,
    ):
        top_left = number == 1

        pad = Node(
            "pad",
            quote(number),
            "thru_hole",
            "roundrect" if top_left else "circle",
            _position_node("at", position),
            Node("size", _MOUNT_SIZE, _MOUNT_SIZE),
            Node("drill", _MOUNT_DRILL),
        )

        if top_left:
            pad.append(Node("roundrect_rratio", _PAD_DIAMETER / 2 / _MOUNT_SIZE))

        root.append(pad)

    return f"{root.serialize()}\n"


def _position_node(name: str, position: Vector2D) -> Node:
    return Node(name, format_decimal(position.x, 6), format_decimal(position.y, 6))


def _graphic_node(name: str, layer: str, stroke_width: float, *attributes: Attribute) -> Node:
    return Node(
        name,
        *attributes,
        Node("stroke", Node("width", stroke_width)),
        Node("fill", False),
        Node("layer", quote(layer)),
    )


if __name__ == "__main__":
    _main()
