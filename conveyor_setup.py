import omni.usd
import carb

from enum import Enum

class TrackType(Enum):
    NORMAL = 0
    CROSS = 1

# helper methods to extract conveyor track related details.
def collect_track_details_from_stage(track_group):
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        print("Invalid stage")
        return {}
    parent_prim = stage.GetPrimAtPath(track_group)
    if not parent_prim.IsValid():
        carb.log_info(f"[ConveyorTracksController]:No prim found at {track_group}")
        return {}

    tracks = {}
    prims = parent_prim.GetChildren()
    for prim in prims:
        for child in prim.GetChildren():
            name = child.GetName()
            if name == "Rollers":
                print(f"conveyor_prim path - {child.GetPath().pathString}")
                tracks[prim.GetPath().pathString] = (child, TrackType.NORMAL)
            if name == "Sorter":
                conveyor_prim = child.GetChild("Sorter_physics")
                if conveyor_prim.IsValid():
                    print(f"conveyor_prim path - {conveyor_prim.GetPath().pathString}")
                    tracks[prim.GetPath().pathString] = (conveyor_prim, TrackType.CROSS)
    return tracks
