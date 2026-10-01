from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Vector3D:
    x: float
    y: float
    z: float

    def __add__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def flatten(self) -> Vector2D:
        return Vector2D(self.x, self.y)


@dataclass(frozen=True)
class Vector2D:
    x: float
    y: float

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x / scalar, self.y / scalar)

    def distance(self, other: Vector2D | None = None) -> float:
        if other is None:
            other = Vector2D(0, 0)

        return sqrt(self.distance_squared(other))

    def distance_squared(self, other: Vector2D) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy


@dataclass(frozen=True)
class Segment2D:
    start: Vector2D
    end: Vector2D


@dataclass(frozen=True, order=True)
class GridVector2D:
    x: int
    y: int

    def __add__(self, other: GridVector2D) -> GridVector2D:
        return GridVector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: GridVector2D) -> GridVector2D:
        return GridVector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: int) -> GridVector2D:
        return GridVector2D(self.x * scalar, self.y * scalar)

    def __floordiv__(self, scalar: int) -> GridVector2D:
        return GridVector2D(self.x // scalar, self.y // scalar)

    def neighbors(self) -> list[GridVector2D]:
        return [
            GridVector2D(self.x + dx, self.y + dy)
            for dx in range(-1, 2)
            for dy in range(-1, 2)
            if dx != 0 or dy != 0
        ]

    def scale(self, scale: float) -> Vector2D:
        return Vector2D(self.x * scale, self.y * scale)


@dataclass(frozen=True)
class GridSegment2D:
    a: GridVector2D
    b: GridVector2D

    def __post_init__(self) -> None:
        a, b = sorted((self.a, self.b))
        object.__setattr__(self, "a", a)
        object.__setattr__(self, "b", b)

    def displacement(self) -> GridVector2D:
        return self.b - self.a

    def midpoint(self) -> Vector2D:
        total = self.a + self.b
        return Vector2D(total.x, total.y) / 2
