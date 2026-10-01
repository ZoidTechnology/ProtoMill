from protomill.cam.slots import Slots
from protomill.geometry import GridSegment2D, Segment2D, Vector2D
from protomill.substrate.geometry import UNIT, Side


class Cuts:
    def __init__(self, cuts: set[GridSegment2D]) -> None:
        self._cuts = cuts

    def slots(self, slot_length: float) -> dict[Side, Slots]:
        slots: dict[Side, list[Segment2D]] = {side: [] for side in Side}

        for cut in self._cuts:
            displacement = cut.displacement()
            perpendicular = Vector2D(-displacement.y, displacement.x)

            if displacement.y <= 0:
                perpendicular *= -1

            midpoint = cut.midpoint()
            offset = perpendicular / perpendicular.distance() * (slot_length / UNIT / 2)

            slots[Side.from_segment(cut)].append(Segment2D(midpoint - offset, midpoint + offset))

        return {side: Slots(slots) for side, slots in slots.items()}
