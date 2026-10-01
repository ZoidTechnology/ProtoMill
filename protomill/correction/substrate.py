from collections.abc import Iterable
from math import sqrt

from protomill.cnc.controller import Controller
from protomill.cnc.gcode import probe, rapid_move
from protomill.cnc.routines import find_center, wait_idle
from protomill.correction.fixture import FixtureCorrection
from protomill.correction.transform import Transform
from protomill.errors import UserError
from protomill.geometry import GridVector2D, Vector2D, Vector3D
from protomill.substrate.geometry import UNIT, Side, flip
from protomill.utility import format_decimal


_FEED = 50
_TOLERANCE = 1
_PROBE_DEPTH = 0.1
_ERROR_THRESHOLD = 0.05

_SUBSTRATE_THICKNESS = 1.6
_MOUNT_RADIUS = 1.75


class SubstrateCorrection:
    TRAVEL_HEIGHT = 0.5

    def __init__(self) -> None:
        self._transform: Transform | None = None

    async def probe(
        self,
        size: GridVector2D,
        mounts: Iterable[GridVector2D],
        side: Side,
        fixture_correction: FixtureCorrection,
        controller: Controller,
    ) -> None:
        def to_physical(position: Vector2D) -> Vector3D:
            position = flip(position, side) * UNIT

            return fixture_correction.apply(
                Vector2D(
                    position.x + fixture_correction.SUBSTRATE_OFFSET.x,
                    -position.y + fixture_correction.SUBSTRATE_OFFSET.y,
                )
            )

        def to_relative_z(position: Vector3D) -> float:
            return position.z + fixture_correction.SUBSTRATE_OFFSET.z + _SUBSTRATE_THICKNESS

        center = size.scale(0.5)
        feed = _FEED
        mount_travel_z = None
        points: list[tuple[Vector2D, Vector3D]] = []

        for mount in mounts:
            if mount_travel_z is not None:
                await controller.send(rapid_move(z=mount_travel_z))

            mount_ideal = mount.scale(1)
            offset = Vector2D(
                -1 if mount.x < center.x else 1, -1 if mount.y < center.y else 1
            ) / sqrt(2)
            physical_z = 0

            for probe_ideal in (mount_ideal + offset, mount_ideal - offset):
                probe_physical = to_physical(probe_ideal)
                probe_relative_z = to_relative_z(probe_physical)
                probe_travel_z = probe_relative_z + _TOLERANCE

                if feed is None:
                    await controller.send(
                        rapid_move(probe_physical.x, probe_physical.y, probe_travel_z)
                    )
                else:
                    await controller.send(
                        rapid_move(
                            probe_physical.x,
                            probe_physical.y,
                            probe_physical.z + fixture_correction.TRAVEL_HEIGHT,
                        )
                    )
                    await controller.send(rapid_move(z=probe_travel_z))

                physical_z += (
                    await controller.probe(probe(z=probe_relative_z - _TOLERANCE, feed=feed))
                ).z
                await controller.send(rapid_move(z=probe_travel_z))

                feed = None

            physical_z /= 2
            mount_physical = to_physical(mount_ideal)
            mount_travel_z = to_relative_z(mount_physical) + _TOLERANCE

            await controller.send(rapid_move(mount_physical.x, mount_physical.y, mount_travel_z))
            await controller.send(rapid_move(z=physical_z - _PROBE_DEPTH))
            physical_xy = await find_center(
                controller, mount_physical.flatten(), _MOUNT_RADIUS + _TOLERANCE
            )

            points.append((mount_ideal, Vector3D(physical_xy.x, physical_xy.y, physical_z)))

        self._transform = Transform(points)

        if self._transform.error > _ERROR_THRESHOLD:
            raise UserError(
                f"Substrate correction error of {format_decimal(self._transform.error)} mm exceeds threshold of {format_decimal(_ERROR_THRESHOLD)} mm."
            )

        await controller.send(rapid_move(z=self.apply(points[-1][0]).z + self.TRAVEL_HEIGHT))
        await wait_idle(controller)

    def apply(self, ideal: Vector2D) -> Vector3D:
        if self._transform is None:
            raise RuntimeError("Substrate correction has no transform")

        return self._transform.apply(ideal)
