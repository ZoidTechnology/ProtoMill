from itertools import pairwise
from math import sqrt

from protomill.geometry import Vector2D
from protomill.identity import NAME
from protomill.substrate.naming import FOOTPRINT_PREFIX, SYMBOL_NAME
from protomill.utility import format_decimal
from tools.kicad import Attribute, Node, property_node, quote
from tools.utility import BUILD_DIRECTORY


_UNIT = 0.254

_MOUNT_OFFSET = 5
_MOUNT_PAD_RADIUS = 4
_MOUNT_PAD_CORNER_OFFSET = Vector2D(_MOUNT_PAD_RADIUS, _MOUNT_PAD_RADIUS)
_MOUNT_PAD_CORNER_RADIUS = 1
_MOUNT_HOLE_RADIUS = 2

_EDGE_OFFSET = 11

_PIN_X_OFFSET = 20
_PROPERTY_Y_OFFSET = 15


def _main() -> None:
    BUILD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    file = BUILD_DIRECTORY / f"{NAME}.kicad_sym"
    file.write_text(_build_symbol_library())


def _build_symbol_library() -> str:
    graphics = _symbol_node("_0_1")
    pins = _symbol_node("_1_1")

    for number, direction in enumerate((Vector2D(x, y) for y in (-1, 1) for x in (-1, 1)), 1):
        position = direction * _MOUNT_OFFSET

        graphics.append(
            Node("circle", _position_node("center", position), _radius_node(_MOUNT_HOLE_RADIUS))
        )

        if number == 1:
            graphics.append(
                Node(
                    "rectangle",
                    _position_node("start", position - _MOUNT_PAD_CORNER_OFFSET),
                    _position_node("end", position + _MOUNT_PAD_CORNER_OFFSET),
                    _radius_node(_MOUNT_PAD_CORNER_RADIUS),
                )
            )
        else:
            graphics.append(
                Node("circle", _position_node("center", position), _radius_node(_MOUNT_PAD_RADIUS))
            )

        pins.append(
            Node(
                "pin",
                "passive",
                "line",
                _position_node(
                    "at",
                    Vector2D(direction.x * _PIN_X_OFFSET, position.y),
                    0 if direction.x < 0 else 180,
                ),
                Node("length", (_PIN_X_OFFSET - _EDGE_OFFSET) * _UNIT),
                Node("number", quote(number)),
            )
        )

    endpoints: list[tuple[Vector2D, Vector2D]] = []
    fill = Node("pts")

    for index, start_direction in enumerate(
        (Vector2D(-1, 0), Vector2D(0, -1), Vector2D(1, 0), Vector2D(0, 1))
    ):
        end_direction = Vector2D(-start_direction.y, start_direction.x)
        corner_direction = start_direction + end_direction

        radius = _EDGE_OFFSET - _MOUNT_OFFSET

        if index == 0:
            radius -= _MOUNT_PAD_RADIUS - _MOUNT_PAD_CORNER_RADIUS

        center = corner_direction * (_EDGE_OFFSET - radius)
        start = center + start_direction * radius
        end = center + end_direction * radius

        graphics.append(
            Node(
                "arc",
                _position_node("start", start),
                _position_node("mid", center + corner_direction * radius / sqrt(2)),
                _position_node("end", end),
                Node("fill", Node("type", "background")),
            )
        )

        endpoints.append((start, end))

        for point in (start, center, end):
            fill.append(_position_node("xy", point))

    for (_, end), (start, _) in pairwise((*endpoints, endpoints[0])):
        graphics.append(
            Node("polyline", Node("pts", _position_node("xy", end), _position_node("xy", start)))
        )

    graphics.append(
        Node(
            "polyline",
            fill,
            Node("stroke", Node("width", -0.0001)),
            Node("fill", Node("type", "background")),
        )
    )

    root = Node(
        "kicad_symbol_lib",
        Node("version", 20251024),
        Node("generator", quote(NAME.lower())),
        _symbol_node(
            "",
            property_node(
                "Reference", "A", _position_node("at", Vector2D(0, -_PROPERTY_Y_OFFSET), 0)
            ),
            property_node(
                "Value", SYMBOL_NAME, _position_node("at", Vector2D(0, _PROPERTY_Y_OFFSET), 0)
            ),
            property_node("ki_fp_filters", f"{FOOTPRINT_PREFIX}*"),
            graphics,
            pins,
        ),
    )

    return f"{root.serialize()}\n"


def _position_node(name: str, position: Vector2D, rotation: int | None = None) -> Node:
    node = Node(name, format_decimal(position.x * _UNIT, 4), format_decimal(-position.y * _UNIT, 4))

    if rotation is not None:
        node.append(rotation)

    return node


def _radius_node(radius: float) -> Node:
    return Node("radius", radius * _UNIT)


def _symbol_node(suffix: str, *attributes: Attribute) -> Node:
    return Node("symbol", quote(f"{SYMBOL_NAME}{suffix}"), *attributes)


if __name__ == "__main__":
    _main()
