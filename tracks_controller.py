import omni
import omni.usd
import omni.graph.core as og
from pxr import Gf

import carb

from pxr import Sdf

class ConveyorTracksController:
    """
    handles setting direction and speed for each conveyor track. it is low level and doesn't handle the behavior logic. 
    1. tracks, involving cross transfer, are driven using physxsurfacevelocityapi schema.
    2. tracks that only move in one direction during operation are driven by omnigraph nodes (because of the simplicity of the existing omnigraph nodes).
    nothing stops one from choosing either one of the methods for all tracks!
    """
    def __init__(self, prefix_path):
        self._stage = omni.usd.get_context().get_stage()
        self._tracks = []
        self._graphs = []

        parent_prim = self._stage.GetPrimAtPath(prefix_path)
        if not parent_prim.IsValid():
            carb.log_info(f"[ConveyorTracksController]:No prim found at '{prefix_path}' — tracks not loaded yet.")
            return

        self._tracks = list(parent_prim.GetChildren())
        self._cross_tracks = set()

        carb.log_info(f"Found {len(self._tracks)} tracks!")

        self.create_graphs_for_tracks()

    def create_action_graph(self, graph_name, conveyor_rigid_prim):
        carb.log_info(f"create_action_graph=({conveyor_rigid_prim})")
        result, graph_prim = omni.kit.commands.execute(
            "CreateConveyorBelt",
            prim_name=graph_name,
            conveyor_prim=conveyor_rigid_prim
        )
        if graph_prim is None:
            carb.log_error(f"Failed to create graph {graph_name}")
            return None

        try:
            dir_attr = graph_prim.GetAttribute("inputs:direction")
            dir_attr.Set(Gf.Vec3f(*[1.0, 0.0, 0.0]))
            attr = graph_prim.GetAttribute("inputs:velocity")
            attr.Set(1.0)
        except Exception as e:
            carb.log_error(f"Failed to set node attributes:{e}")
            return None
        carb.log_info(f"create_action_graph-{graph_name}: Success")
        return graph_prim


    def create_graphs_for_tracks(self):
        """
        create omnigraph for each track containing
        three nodes: onTick, conveyorBelt, velocity, direction.
        """
        for track in self._tracks:
            track_path = track.GetPath().pathString
            graph_prim_path = f"{track_path}/ConveyorTrackGraph"
            graph_name = "ConveyorTrackGraph"

            # Remove any existing graph to avoid duplicates
            if self._stage.GetPrimAtPath(graph_prim_path).IsValid():
                carb.log_info(f"Replacing existing ActionGraph under {track_path}")
                self._stage.RemovePrim(graph_prim_path)

            conveyor_rigid_prim = self.find_rigid_prim_for_conveyor_belt_node(track)
            if conveyor_rigid_prim is None:
                carb.log_warn(f"There is no roller or sorter material for track {track_path}")
                continue

            # Create the ActionGraph prim
            graph_prim = self.create_action_graph(graph_name, conveyor_rigid_prim)

            self._graphs.append(graph_prim)
            carb.log_info(f"Created ActionGraph for {track_path}.")

    def find_rigid_prim_for_conveyor_belt_node(self, track_prim):
        """Return the target prim path that should be driven by the conveyor node."""
        for child in track_prim.GetChildren():
            name = child.GetName()
            if name == "Rollers":
                return child
            if name == "Sorter":
                conveyor_prim = child.GetChild("Sorter_physics")
                if conveyor_prim.IsValid():
                    self._cross_tracks.add(track_prim)
                    return conveyor_prim
        return None


    def get_tracks(self):
        return self._tracks
