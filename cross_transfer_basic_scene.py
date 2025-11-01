from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

from isaacsim.core.utils.extensions import enable_extension

# Enable Conveyor extension
enable_extension("isaacsim.asset.gen.conveyor")

import sys
import numpy as np
from isaacsim.core.api import World
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.sensors.physics import ContactSensor
from pxr import UsdGeom, Gf, PhysxSchema
import omni.usd
import omni.graph.core as og
from pathlib import Path

current_dir = Path(__file__).parent
asset_root_path = str(current_dir / "assets")

### all prim paths of interest. Better to write high level manager classes
# to collect and manage all the details. Keeping it here for simplicity for now.
world_prefix = "/World"
middle_parent = "/sensor_base_01"
tracks = [f"/World/ConveyorTrack_{i:02d}" for i in range(1, 5)]
track_directions = [-1, 1, 1] # This list maps to tracks list,

def create_contact_sensor(parent_prim, sensor_prim_name):
    prim_full_path = parent_prim + sensor_prim_name
    sensor = ContactSensor(
        prim_path=prim_full_path,
        name=sensor_prim_name,
        frequency=60
    )

    return sensor

def is_sensor_in_contact(sensor_prim):
    # Later: expand the condition further like checking minimum force value etc.
    return sensor_prim.get_current_frame()["in_contact"]

def conveyor_track_set_surface_velocity(prim_path, vel):
    stage = omni.usd.get_context().get_stage()
    sorter_prim = stage.GetPrimAtPath(prim_path)
    surface_velocity_api = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(sorter_prim)
    if surface_velocity_api:
        surface_velocity_api.GetSurfaceVelocityAttr().Set(Gf.Vec3f(*vel))
    else:
        print("Prim does not have PhysxSurfaceVelocityAPI applied.")

##################################################
def check_validity_of_prims_of_interest():
    stage = omni.usd.get_context().get_stage()
    all_paths = trackA_graph_paths + trackB_graph_paths + [middle_parent, cross_track_sorter_prim_path]
    for prim_path in all_paths:
        if not stage.GetPrimAtPath(prim_path).IsValid():
            print(f"Invalid prim path {prim_path}")
            return False

    return True

my_world = World(stage_units_in_meters=1.0)
my_world.scene.add_default_ground_plane()
asset_path = asset_root_path + "/conveyor_room.usd"

setup = add_reference_to_stage(usd_path=asset_path, prim_path="/World/")

### sanity check on usd file
if not check_validity_of_prims_of_interest():
    simulation_app.close()
    sys.exit(1)

# create contact sensor and place it in the centre of the junction
middle_sensor = create_contact_sensor(middle_parent, "middle_sensor_1")

my_world.reset()
my_world.play()

# probably needed to wait for og graphs to initialize
for _ in range(3):
    my_world.step(render=True)

# put all conveyor belts to moving state
conveyor_tracks_set_velocity(speed=0.5)

step_count = 0

while simulation_app.is_running():

    if is_sensor_in_contact(middle_sensor):
        # change direction - TODO use rotate operator
        conveyor_track_set_cross_velocity(cross_track_sorter_prim_path, [0.0, 0.5, 0.0])

    my_world.step(render=True)

    step_count += 1
    if step_count >= 500:
        break

simulation_app.close()
