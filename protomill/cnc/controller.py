from abc import ABC, abstractmethod
from asyncio import create_task, sleep
from collections.abc import Callable
from dataclasses import dataclass
from logging import getLogger

from serial import Serial, SerialException

from protomill.errors import UserError
from protomill.geometry import Vector3D
from protomill.utility import chain_error, escape_string


_POLL_INTERVAL = 0.01

_logger = getLogger(__name__)


@dataclass(frozen=True)
class StatusResponse:
    idle: bool
    position: Vector3D
    probe: bool
    buffer: int | None


class Controller(ABC):
    def __init__(self, port: Serial, on_error: Callable[[Exception], object]) -> None:
        if port.timeout != 0 or port.write_timeout != 0:
            raise RuntimeError("Port read and write timeouts must be zero")

        self._port = port
        self._on_error = on_error
        self._read_buffer = bytearray()
        self._write_buffer = bytearray()
        self._poll_task = create_task(self._poll())
        self._stopping = False

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def status(self) -> StatusResponse:
        pass

    @abstractmethod
    async def send(self, line: str) -> None:
        pass

    @abstractmethod
    async def probe(self, line: str) -> Vector3D:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        self._stopping = True
        await self._poll_task

    @abstractmethod
    def _on_line(self, line: str) -> None:
        pass

    @abstractmethod
    def _on_poll_error(self, error: Exception) -> None:
        pass

    def _write(self, string: str) -> None:
        if self._stopping or self._poll_task.done():
            raise RuntimeError("Controller is not running")

        string = string.replace(" ", "")
        _logger.info("Sending %s", escape_string(string))
        self._write_buffer += string.encode("ascii")

    async def _poll(self) -> None:
        try:
            while True:
                self._read_buffer += self._port.read_all() or b""

                while b"\n" in self._read_buffer:
                    raw_line, self._read_buffer = self._read_buffer.split(b"\n", 1)
                    line = raw_line.decode("ascii").strip()
                    _logger.info("Received %s", escape_string(line))
                    self._on_line(line)

                if self._write_buffer:
                    written = self._port.write(self._write_buffer)
                    del self._write_buffer[:written]

                if self._stopping and not self._write_buffer:
                    return

                await sleep(_POLL_INTERVAL)
        except SerialException as error:
            self._on_poll_error(
                chain_error(UserError("Failed to communicate with the CNC machine."), error)
            )
        except Exception as error:  # noqa: BLE001
            self._on_poll_error(error)
