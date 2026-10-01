from protomill.cnc.controller import Controller
from protomill.cnc.gcode import probe, rapid_move
from protomill.cnc.routines import find_center, wait_idle
from protomill.correction.transform import Transform
from protomill.errors import UserError
from protomill.geometry import Vector2D, Vector3D
from protomill.utility import format_decimal


_FEED = 100
_TOLERANCE = 5
_INITIAL_PROBE_DISTANCE = 20
_PROBE_DEPTH = 0.5
_ERROR_THRESHOLD = 0.1

_PROTRUSION_HEIGHT = 5
_FEATURE_RADIUS = 7.5
_FEATURE_DEPTH = 3.5
_FEATURE_DISTANCE_X = 131.6
_FEATURE_DISTANCE_Y = 142
_FEATURE_OFFSETS = (
    Vector2D(0, 0),
    Vector2D(_FEATURE_DISTANCE_X, 0),
    Vector2D(0, -_FEATURE_DISTANCE_Y),
    Vector2D(-_FEATURE_DISTANCE_X, 0),
)


class FixtureCorrection:
    TRAVEL_HEIGHT = _PROTRUSION_HEIGHT + 1
    SUBSTRATE_OFFSET = Vector3D(15, -4.85, 0)

    def __init__(self) -> None:
        self._transform: Transform | None = None

    async def probe(self, position: Vector3D, controller: Controller) -> None:
        points: list[tuple[Vector2D, Vector3D]] = []
        ideal = Vector2D(0, 0)
        physical_xy = position.flatten()
        physical_z = position.z
        probe_distance = _INITIAL_PROBE_DISTANCE
        feed = _FEED

        for offset in _FEATURE_OFFSETS:
            ideal += offset
            physical_xy += offset

            if points:
                await controller.send(rapid_move(z=physical_z + _PROTRUSION_HEIGHT + _TOLERANCE))
                await controller.send(rapid_move(physical_xy.x, physical_xy.y))
                await controller.send(rapid_move(z=physical_z - _FEATURE_DEPTH + _TOLERANCE))

                probe_distance = _FEATURE_DEPTH + _TOLERANCE
                feed = None

            physical_z = (
                await controller.probe(probe(z=physical_z - probe_distance, feed=feed))
            ).z + _FEATURE_DEPTH
            await controller.send(rapid_move(z=physical_z - _PROBE_DEPTH))
            physical_xy = await find_center(controller, physical_xy, _FEATURE_RADIUS + _TOLERANCE)

            points.append((ideal, Vector3D(physical_xy.x, physical_xy.y, physical_z)))

        self._transform = Transform(points)

        if self._transform.error > _ERROR_THRESHOLD:
            raise UserError(
                f"Fixture correction error of {format_decimal(self._transform.error)} mm exceeds threshold of {format_decimal(_ERROR_THRESHOLD)} mm."
            )

        await controller.send(rapid_move(z=self.apply(ideal).z + self.TRAVEL_HEIGHT))
        await wait_idle(controller)

    def apply(self, ideal: Vector2D) -> Vector3D:
        return self._require_transform().apply(ideal)

    def apply_inverse(self, physical: Vector2D) -> Vector2D:
        return self._require_transform().apply_inverse(physical)

    def _require_transform(self) -> Transform:
        if self._transform is None:
            raise RuntimeError("Fixture correction has no transform")

        return self._transform
