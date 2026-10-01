from dataclasses import dataclass

from kipy.board import Board
from kipy.board_types import ArcTrack, LeaderDimension, Pad, Track, Via, Zone
from kipy.geometry import Vector2
from kipy.proto.board.board_types_pb2 import BoardLayer, DimensionTextBorderStyle
from kipy.proto.common.types import HorizontalAlignment, KiCadObjectType
from kipy.util.units import from_mm

from protomill.cam.layout import Layout
from protomill.errors import UserError
from protomill.geometry import GridSegment2D, GridVector2D
from protomill.substrate.footprint import SubstrateFootprint
from protomill.substrate.geometry import SUBSTRATE_SIZES, UNIT, SubstrateGeometry


_GRID_PITCH = from_mm(UNIT)

_MARKER_LAYER = BoardLayer.BL_Cmts_User
_MARKER_PREFIX = "\u200b"


@dataclass(frozen=True)
class Violation:
    message: str
    position: Vector2


class DesignError(UserError):
    def __init__(self, violations: list[Violation]) -> None:
        unique = {
            (violation.position.x, violation.position.y, violation.message): violation
            for violation in violations
        }
        self.violations = list(unique.values())
        count = len(self.violations)

        if count == 1:
            super().__init__(
                "The design contains a violation. The violation has been marked in KiCad."
            )
        else:
            super().__init__(
                f"The design contains {count} violations. The violations have been marked in KiCad."
            )


class Design:
    def __init__(self, board: Board) -> None:
        self._board = board
        self._items = board.get_items(
            (
                KiCadObjectType.KOT_PCB_ARC,
                KiCadObjectType.KOT_PCB_FOOTPRINT,
                KiCadObjectType.KOT_PCB_PAD,
                KiCadObjectType.KOT_PCB_TRACE,
                KiCadObjectType.KOT_PCB_VIA,
                KiCadObjectType.KOT_PCB_ZONE,
            )
        )

    def layout(self, tolerance: float) -> Layout:
        substrate_footprints = SubstrateFootprint.from_items(self._items)

        if not substrate_footprints:
            raise UserError("A substrate footprint was not found in the design.")

        if len(substrate_footprints) > 1:
            raise UserError("More than one substrate footprint was found in the design.")

        substrate_footprint = substrate_footprints[0]
        substrate_bounds = substrate_footprint.bounds()

        if substrate_bounds is None:
            raise UserError("The bounds of the substrate footprint could not be determined.")

        def snap(position: Vector2) -> GridVector2D | None:
            relative = position - substrate_bounds.pos

            grid_x = relative.x / _GRID_PITCH
            grid_y = relative.y / _GRID_PITCH

            nearest_x = round(grid_x)
            nearest_y = round(grid_y)

            error = max(abs(grid_x - nearest_x), abs(grid_y - nearest_y))

            if error > tolerance / 2:
                return None

            return GridVector2D(nearest_x, nearest_y)

        substrate_size = snap(substrate_bounds.pos + substrate_bounds.size)

        if substrate_size is None:
            raise UserError("The bounds of the substrate footprint do not align with the grid.")

        if substrate_size not in SUBSTRATE_SIZES:
            raise UserError("The size of the substrate footprint is not supported.")

        violations: list[Violation] = []
        substrate_pads = substrate_footprint.pads()
        substrate_geometry = SubstrateGeometry.from_size(substrate_size)
        pads: set[GridVector2D] = set()
        front_endpoints: set[GridVector2D] = set()
        back_endpoints: set[GridVector2D] = set()
        tracks: set[GridSegment2D] = set()

        for item in self._items:
            match item:
                case Pad() | Via():
                    if item.id.value in substrate_pads:
                        continue

                    position = snap(item.position)

                    if position is None:
                        violations.append(Violation("Pad or via is not on the grid", item.position))
                        continue

                    if position not in substrate_geometry.pads:
                        violations.append(
                            Violation("Pad or via is not over a substrate hole", item.position)
                        )
                        continue

                    pads.add(position)
                case Track():
                    midpoint = (item.start + item.end) * 0.5

                    if item.layer == BoardLayer.BL_F_Cu:
                        endpoints = front_endpoints
                    elif item.layer == BoardLayer.BL_B_Cu:
                        endpoints = back_endpoints
                    else:
                        violations.append(Violation("Track is not on an outer layer", midpoint))
                        continue

                    start = snap(item.start)
                    end = snap(item.end)

                    if start is None or end is None:
                        violations.extend(
                            Violation("Track endpoint is not on the grid", source)
                            for source, snapped in ((item.start, start), (item.end, end))
                            if snapped is None
                        )
                        continue

                    displacement = end - start

                    if (
                        displacement.x != 0
                        and displacement.y != 0
                        and abs(displacement.x) != abs(displacement.y)
                    ):
                        violations.append(
                            Violation("Track angle is not a multiple of 45°", midpoint)
                        )
                        continue

                    segments = max(abs(displacement.x), abs(displacement.y))

                    if segments == 0:
                        violations.append(Violation("Track has zero length", midpoint))
                        continue

                    segment_displacement = displacement // segments

                    for segment in range(segments):
                        track = GridSegment2D(
                            start + segment_displacement * segment,
                            start + segment_displacement * (segment + 1),
                        )

                        if (
                            track not in substrate_geometry.tracks
                            and track not in substrate_geometry.mount_internals
                        ):
                            violations.append(
                                Violation(
                                    "Track segment is not over a substrate trace",
                                    item.start
                                    + (item.end - item.start) * ((segment + 0.5) / segments),
                                )
                            )
                            continue

                        endpoints.update((track.a, track.b))
                        tracks.add(track)
                case ArcTrack():
                    violations.append(Violation("Arc tracks are not supported", item.mid))
                case Zone():
                    violations.append(
                        Violation("Zones are not supported", item.bounding_box().center())
                    )

        if violations:
            raise DesignError(violations)

        for transition in (front_endpoints & back_endpoints) - pads:
            violations.append(
                Violation(
                    "Front and back tracks meet at a substrate hole",
                    Vector2.from_xy(transition.x * _GRID_PITCH, transition.y * _GRID_PITCH)
                    + substrate_bounds.pos,
                )
            )

        if violations:
            raise DesignError(violations)

        return Layout(substrate_geometry, pads | front_endpoints | back_endpoints, tracks)

    def update_markers(self, violations: list[Violation]) -> None:
        old_markers = [
            marker
            for marker in self._board.get_dimensions()
            if isinstance(marker, LeaderDimension)
            and marker.layer == _MARKER_LAYER
            and marker.override_text.startswith(_MARKER_PREFIX)
        ]

        offset = _GRID_PITCH // 4
        feature_size = offset // 2
        thickness = feature_size // 5
        new_markers: list[LeaderDimension] = []

        for violation in violations:
            marker = LeaderDimension()

            marker.layer = _MARKER_LAYER

            marker.start = violation.position
            marker.end = marker.start + Vector2.from_xy(offset, -offset)
            marker.text.position = marker.end + Vector2.from_xy(offset, 0)

            marker.override_text = _MARKER_PREFIX + violation.message
            marker.override_text_enabled = True

            marker.arrow_length = feature_size
            marker.line_thickness = thickness
            marker.border_style = DimensionTextBorderStyle.DTBS_RECTANGLE

            attributes = marker.text.attributes

            attributes.size = Vector2.from_xy(feature_size, feature_size)
            attributes.stroke_width = thickness
            attributes.horizontal_alignment = HorizontalAlignment.HA_LEFT

            new_markers.append(marker)

        if old_markers or new_markers:
            commit = self._board.begin_commit()

            try:
                self._board.remove_items(old_markers)
                self._board.create_items(new_markers)
            except:
                self._board.drop_commit(commit)
                raise

            self._board.push_commit(commit, "Update Violation Markers")
