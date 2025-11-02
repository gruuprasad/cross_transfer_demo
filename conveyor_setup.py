import omni.usd
import carb

import json
from pathlib import Path
from enum import Enum

class TrackType(Enum):
    NORMAL = 0
    CROSS = 1

def merge_config_with_tracks(tracks, config_file="config.json"):
    config_path = Path(__file__).resolve().parent / "config" / config_file

    # Load config (can be missing or empty)
    if not config_path.exists():
        print(f"[config] File not found: {config_path}, skipping merge.")
        return tracks

    try:
        with config_path.open("r") as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[config] Invalid JSON: {e}")
        return tracks

    # Merge config directions into existing track dict
    for name, track in tracks.items():
        if name in config_data:
            cfg = config_data[name]
            if "directions" in cfg and isinstance(cfg["directions"], list):
                track["directions"] = cfg["directions"]
                print(f"[config] Merged directions for {name}: {cfg['directions']}")
            else:
                print(f"[config] No valid directions for {name}")
        else:
            print(f"[config] No config entry for {name}")

    return tracks

# helper methods to extract conveyor track related details.
def read_track_details(parent_prim_path):
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        print("Invalid stage")
        return {}
    parent_prim = stage.GetPrimAtPath(parent_prim_path)
    if not parent_prim.IsValid():
        carb.log_info(f"No prim found at {parent_prim_path}")
        return {}

    tracks = {}
    prims = parent_prim.GetChildren()
    for prim in prims:
        for child in prim.GetChildren():
            name = child.GetName()
            if name == "Rollers":
                print(f"conveyor_prim path - {child.GetPath().pathString}")
                tracks[prim.GetPath().pathString] = {"type": TrackType.NORMAL, "rigid_prim": child}
            if name == "Sorter":
                conveyor_prim = child.GetChild("Sorter_physics")
                if conveyor_prim.IsValid():
                    print(f"conveyor_prim path - {conveyor_prim.GetPath().pathString}")
                    tracks[prim.GetPath().pathString] = {"type": TrackType.CROSS, "rigid_prim": conveyor_prim}

    return merge_config_with_tracks(tracks)
