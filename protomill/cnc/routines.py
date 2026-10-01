from asyncio import TaskGroup, sleep
from collections.abc import Callable

from protomill.cnc.controller import Controller, StatusResponse
from protomill.cnc.gcode import probe, rapid_move
from protomill.geometry import Vector2D


async def find_center(
    controller: Controller, position: Vector2D, distance: float, feed: float | None = None
) -> Vector2D:
    right = await controller.probe(probe(position.x + distance, feed=feed))
    await controller.send(rapid_move(position.x))
    left = await controller.probe(probe(position.x - distance))

    center_x = (right.x + left.x) / 2
    await controller.send(rapid_move(center_x))

    up = await controller.probe(probe(y=position.y + distance))
    await controller.send(rapid_move(y=position.y))
    down = await controller.probe(probe(y=position.y - distance))

    center_y = (up.y + down.y) / 2
    await controller.send(rapid_move(y=center_y))

    return Vector2D(center_x, center_y)


async def poll_status(
    controller: Controller, on_status: Callable[[StatusResponse], bool], interval: float = 0.1
) -> StatusResponse:
    while True:
        status = await controller.status()

        if on_status(status):
            return status

        await sleep(interval)


async def stream(
    controller: Controller,
    lines: list[str],
    buffer_size: int | None,
    on_progress: Callable[[float], None],
) -> None:
    total = len(lines)
    sent = 0
    executed = 0

    async def send() -> None:
        nonlocal sent

        for line in lines:
            await controller.send(line)
            sent += 1

    def on_status(status: StatusResponse) -> bool:
        nonlocal executed

        if buffer_size is None or status.buffer is None:
            buffered = 0
        else:
            buffered = buffer_size - status.buffer

        executed = max(executed, sent - buffered)
        on_progress(executed / total)

        return sent == total and status.idle

    try:
        async with TaskGroup() as group:
            group.create_task(send())
            group.create_task(poll_status(controller, on_status))
    except ExceptionGroup as group:
        error = group.exceptions[0]
        error.__suppress_context__ = True
        raise error


async def wait_idle(controller: Controller) -> StatusResponse:
    return await poll_status(controller, lambda status: status.idle)


async def wait_probe(controller: Controller) -> StatusResponse:
    return await poll_status(controller, lambda status: status.probe)
