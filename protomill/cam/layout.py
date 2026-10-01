from protomill.cam.cuts import Cuts
from protomill.geometry import GridSegment2D, GridVector2D
from protomill.substrate.geometry import SubstrateGeometry


class Layout:
    def __init__(
        self,
        substrate_geometry: SubstrateGeometry,
        nodes: set[GridVector2D],
        tracks: set[GridSegment2D],
    ) -> None:
        self.substrate_geometry = substrate_geometry
        self._nodes = nodes
        self._tracks = tracks

    def cuts(self) -> Cuts:
        cuts = self.substrate_geometry.mount_entries.copy()

        cuts.update(
            GridSegment2D(point, neighbor)
            for point in self._nodes
            for neighbor in point.neighbors()
        )

        cuts &= self.substrate_geometry.tracks
        cuts -= self._tracks

        return Cuts(cuts)
