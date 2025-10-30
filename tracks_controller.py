import omni.usd
import omni.graph.core as og

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
            print(f"No prim found at '{prefix_path}' — tracks not loaded yet.")
            return

        self._tracks = list(parent_prim.GetChildren())
        self._cross_tracks = set()

        print(f"Found {len(self._tracks)} tracks!")

        self.create_graphs_for_tracks()

    def create_graphs_for_tracks(self):
        """
        create omnigraph for each track containing
        three nodes: onTick, conveyorBelt, velocity, direction.
        """
        for track in self._tracks:
            track_path = track.GetPath().pathString
            graph_path = f"{track_path}/ConveyorTrackGraph"

            # Remove any existing graph to avoid duplicates
            if self._stage.GetPrimAtPath(graph_path).IsValid():
                print(f"Replacing existing ActionGraph under {track_path}")
                self._stage.RemovePrim(graph_path)

            roller_prim_path = self.find_roller_prim_for_conveyor_belt_node(track)
            if roller_prim_path is None:
                print(f"There is no roller or sorter material for track {track_path}")
                continue

            # Create the ActionGraph prim
            print(f"graph_path ={graph_path}")
            print("=== DIAGNOSTIC for this track ===")
            print("track.GetPath().pathString repr:", repr(track_path))
            print("track.GetPath().pathString len:", len(track_path))
            print("graph_path repr:", repr(graph_path))
            print("graph_path endswith '/':", graph_path.endswith("/"))

            # show the code points of the last few characters to reveal hidden chars
            print("last chars (ord):", [(c, ord(c)) for c in graph_path[-6:]])

            # USD validator
            try:
                is_valid = Sdf.Path.IsValidPathString(graph_path)
                print("Sdf.Path.IsValidPathString:", is_valid)
            except Exception as e:
                print("Sdf.Path.IsValidPathString raised:", e)

            og.Controller.edit(
                {
                    "graph_path": graph_path,
                    "evaluator_name": "execution",
                    "pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND,
                }
            )

            print("graph creation SUCCESS")

            # Add OnTick node
            tick_node = og.Controller.create_node(graph_path, "omni.graph.action.OnTick")
            conveyor_node = og.Controller.create_node(graph_path, "isaacsim.asset.gen.conveyor.IsaacConveyor")
            direction = og.Controller.create_node(graph_path, "omni.graph.nodes.ConstantVector3f")
            speed = og.Controller.create_node(graph_path, "omni.graph.nodes.ConstantFloat")

            # --- Configure constants ---
            print("configuring constants for nodes")
            og.Controller.set(og.Controller.attribute(direction, "inputs:value"), [1.0, 0.0, 0.0])
            og.Controller.set(og.Controller.attribute(speed, "inputs:value"), 0.0)
            og.Controller.set(og.Controller.attribute(conveyor_node, "inputs:conveyorPrim"), roller_prim_path)

             # --- Connect ---
            print("connecting nodes")
            og.Controller.connect(og.Controller.attribute(tick_node, "outputs:tick"),
                                  og.Controller.attribute(conveyor_node, "inputs:execIn"))
            og.Controller.connect(og.Controller.attribute(direction, "outputs:value"),
                                  og.Controller.attribute(conveyor_node, "inputs:direction"))
            og.Controller.connect(og.Controller.attribute(speed, "outputs:value"),
                                  og.Controller.attribute(conveyor_node, "inputs:speed"))

            print(f"Created ActionGraph for {track_path}.")
            self._graphs.append(graph_path)

    def find_roller_prim_for_conveyor_belt_node(self, track_prim):
        """Return the target prim path that should be driven by the conveyor node."""
        for child in track_prim.GetChildren():
            name = child.GetName().lower()
            if "rollers" in name:
                return child.GetPath().pathString
            if "sorter" in name:
                self._cross_tracks.add(track_prim)
                return f"{child.GetPath().pathString}/Sorter_physics"
        return None


    def get_tracks(self):
        return self._tracks
