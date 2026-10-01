import numpy

from protomill.geometry import Vector2D, Vector3D


class Transform:
    def __init__(self, points: list[tuple[Vector2D, Vector3D]]) -> None:
        ideal = numpy.array([[point.x, point.y, 1] for point, _ in points])
        physical = numpy.array([[point.x, point.y, point.z] for _, point in points])
        self._transform, residuals, *_ = numpy.linalg.lstsq(ideal, physical)
        self.error = numpy.sqrt(residuals.sum() / len(points))

    def apply(self, ideal: Vector2D) -> Vector3D:
        transformed = numpy.array([ideal.x, ideal.y, 1]) @ self._transform
        return Vector3D(float(transformed[0]), float(transformed[1]), float(transformed[2]))

    def apply_inverse(self, physical: Vector2D) -> Vector2D:
        transformed = numpy.linalg.solve(
            self._transform[:2, :2].T,
            numpy.array([physical.x, physical.y]) - self._transform[2, :2],
        )

        return Vector2D(float(transformed[0]), float(transformed[1]))
