from asyncio import sleep
from time import perf_counter

import numpy

from protomill.cnc.gcode import linear_move, rapid_move
from protomill.correction.substrate import SubstrateCorrection
from protomill.geometry import Segment2D, Vector2D
from protomill.settings import MillingSettings


_YIELD_INTERVAL = 0.01
_YIELD_DURATION = 0.001


class Yielder:
    def __init__(self) -> None:
        self._next = None

    async def check(self) -> None:
        if self._next is not None:
            if perf_counter() < self._next:
                return

            await sleep(_YIELD_DURATION)

        self._next = perf_counter() + _YIELD_INTERVAL


class Slots:
    def __init__(self, slots: list[Segment2D]) -> None:
        self.slots = slots

    async def ordered(self, start: Vector2D) -> Slots:
        slots = self.slots.copy()
        yielder = Yielder()
        position = start
        ordered: list[Segment2D] = []

        while slots:
            await yielder.check()

            best_index = 0
            best_distance = float("inf")

            for index, slot in enumerate(slots):
                distance = position.distance_squared(slot.start)

                if distance < best_distance:
                    best_index = index
                    best_distance = distance

            best_slot = slots.pop(best_index)
            ordered.append(best_slot)
            position = best_slot.end

        return Slots(ordered)

    async def optimized(self, start: Vector2D, end: Vector2D, max_block: int) -> Slots:
        def distances(a: numpy.ndarray, b: numpy.ndarray) -> numpy.ndarray:
            differences = a - b
            return numpy.hypot(differences[..., 0], differences[..., 1])

        improved = True
        yielder = Yielder()
        starts = numpy.array(
            [(0, 0), *((slot.start.x, slot.start.y) for slot in self.slots), (end.x, end.y)]
        )
        ends = numpy.array(
            [(start.x, start.y), *((slot.end.x, slot.end.y) for slot in self.slots), (0, 0)]
        )

        while improved:
            improved = False

            for block_size in range(1, max_block + 1):
                for block_start in range(1, len(starts) - block_size):
                    await yielder.check()

                    block_end = block_start + block_size
                    predecessors = numpy.concatenate((ends[:block_start], ends[block_end:-1]))
                    successors = numpy.concatenate((starts[1:block_start], starts[block_end:]))

                    costs = (
                        distances(predecessors, starts[block_start])
                        + distances(ends[block_end - 1], successors)
                        - distances(predecessors, successors)
                    )

                    improvements = costs[block_start - 1] - costs
                    best = improvements.argmax()

                    if improvements[best] > 1e-9:
                        insertion = best + 1
                        window = slice(
                            min(insertion, block_start), max(insertion, block_start) + block_size
                        )
                        shift = block_size if insertion < block_start else -block_size

                        starts[window] = numpy.roll(starts[window], shift, axis=0)
                        ends[window] = numpy.roll(ends[window], shift, axis=0)

                        improved = True

        return Slots(
            [
                Segment2D(Vector2D(*start), Vector2D(*end))
                for start, end in zip(starts[1:-1].tolist(), ends[1:-1].tolist())
            ]
        )

    def gcode(
        self, correction: SubstrateCorrection, settings: MillingSettings
    ) -> tuple[list[str], Vector2D]:
        lines: list[str] = []
        position = None

        for slot in self.slots:
            start = correction.apply(slot.start)
            end = correction.apply(slot.end)

            for step in range(settings.passes):
                if position is not None:
                    lines.append(rapid_move(z=position.z + correction.TRAVEL_HEIGHT))

                depth = settings.depth / settings.passes * (step + 1)

                lines += (
                    rapid_move(start.x, start.y, start.z + correction.TRAVEL_HEIGHT),
                    linear_move(z=start.z - depth, feed=settings.plunge_rate),
                    linear_move(end.x, end.y, end.z - depth, settings.feed_rate),
                )

                position = end

        if position is None:
            raise RuntimeError("Failed to generate G-code")

        return lines, position.flatten()
