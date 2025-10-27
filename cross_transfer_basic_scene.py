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

# sensor placement locations
middle_parent = "/World/sensor_base_01"
#lborder_parent = "/World/sensor_base_02"
#fborder_parent = "/World/sensor_base_03"

def create_contact_sensor(parent_prim, sensor_prim_name):
    prim_full_path = parent_prim + "/" + sensor_prim_name
    sensor = ContactSensor(
        prim_path=prim_full_path,
        name=sensor_prim_name,
        frequency=60
    )

    return sensor

def is_sensor_in_contact(sensor_prim):
    # Later: expand the condition further like checking minimum force value etc.
    return sensor_prim.get_current_frame()["in_contact"]

#### These prim paths are taken from USD
trackA_graph_paths = [f"/World/ConveyorTrack_A_{i:02d}/ConveyorBeltGraph" for i in range(1, 3)]
trackA_directions = [-1, 1] # temporary fix, assets has to be aligned in uni direction
trackB_graph_paths = [f"/World/ConveyorTrack_B_{i:02d}/ConveyorBeltGraph" for i in range(1, 2)]
trackB_directions = [1] # temporary fix, assets has to be aligned in uni direction
cross_track_sorter_prim_path = "/World/ConveyorTrack_AB_01/Sorter/Sorter_physics"

def conveyor_tracks_set_velocity(speed):
    for graph_path, direction in zip(trackA_graph_paths, trackA_directions):
        graph = og.get_graph_by_path(graph_path)
        graph.find_variable("Velocity").set(graph.get_context(), speed * direction)

    for graph_path, direction in zip(trackB_graph_paths, trackB_directions):
        graph = og.get_graph_by_path(graph_path)
        graph.find_variable("Velocity").set(graph.get_context(), speed * direction)

    conveyor_track_set_cross_velocity(cross_track_sorter_prim_path, [speed, 0.0, 0.0])

def conveyor_track_pause(graph_path):
    graph = og.get_graph_by_path(graph_path)
    graph.find_variable("Velocity").set(graph.get_context(), 0.0)
    #og.Controller.attribute("/World/ConveyorTrack/ConveyorBeltGraph/ConveyorNode.inputs:velocity").set(0.0)

# cross_track
def conveyor_track_set_cross_velocity(sorter_prim_path, vel):
    stage = omni.usd.get_context().get_stage()
    sorter_prim = stage.GetPrimAtPath(sorter_prim_path)
    surface_velocity_api = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(sorter_prim)
    if surface_velocity_api:
        # Get current velocity for debugging
        #current_velocity = surface_velocity_api.GetSurfaceVelocityAttr().Get()

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

setup = add_reference_to_stage(usd_path=asset_path, prim_path="/World")

### sanity check on usd file
if not check_validity_of_prims_of_interest():
    simulation_app.close()
    sys.exit(1)

# temporarily move the cube closer to junction
#stage = omni.usd.get_context().get_stage()
#cube_prim = stage.GetPrimAtPath("/World/Cube")
#current_pos = cube_prim.GetAttribute("xformOp:translate").Get()
#cube_prim.GetAttribute("xformOp:translate").Set((2.4, current_pos[1], current_pos[2]))

# create contact sensor and place it in the centre of the junction
middle_sensor = create_contact_sensor(middle_parent, "middle_sensor_1")
#lborder_sensor = create_contact_sensor(lborder_parent)
#fborder_sensor = create_contact_sensor(fborder_parent)

my_world.reset()
my_world.play()

# probably needed to wait for og graphs to initialize
for _ in range(3):
    my_world.step(render=True)

# put all conveyor belts to moving state
conveyor_tracks_set_velocity(speed=0.5)

step_count = 0

while simulation_app.is_running():
    my_world.step(render=True)

    if is_sensor_in_contact(middle_sensor):
        # TODO box immediately stops, need to position the box in the centre ideally.
        # Box changed direction slowly, not adding the pause.
        # stop the belt -
        #conveyor_track_set_cross_velocity(cross_track_sorter_prim_path, [0.0, 0.0, 0.0])
        #my_world.step(render=True)
        #step_count += 1

        # change direction - TODO use rotate operator
        conveyor_track_set_cross_velocity(cross_track_sorter_prim_path, [0.0, 0.5, 0.0])

    step_count += 1
    if step_count >= 500:
        break

simulation_app.close()

### helper functons
def print_contact_sensor_details(sensor):
    print(f"--------contact sensor data---------------")
    sensor.add_raw_contact_data_to_frame()
    print(sensor.get_current_frame())
    sensor.remove_raw_contact_data_from_frame()
    print("-----------------------")

def read_conveyor_node_parameters():
    conveyor_belt_graph = og.get_graph_by_path("/World/ConveyorTrack/ConveyorBeltGraph")
    # Access a variable by name in the graph
    cur_velocity = og.Controller.find_variable((conveyor_belt_graph, "Velocity"))
    val = cur_velocity.get(conveyor_belt_graph.get_context())
    read_speed_output = og.Controller.attribute("/World/ConveyorTrack/ConveyorBeltGraph/read_speed.outputs:value").get()
    conveyor_node_input = og.Controller.attribute("/World/ConveyorTrack/ConveyorBeltGraph/ConveyorNode.inputs:velocity").get()
    print(f"velocity = {val}, read_speed_output = {read_speed_output}, conveyor_node_input_velocity = {conveyor_node_input}")


