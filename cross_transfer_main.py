from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

from isaacsim.core.utils.extensions import enable_extension
enable_extension("isaacsim.asset.gen.conveyor")

import sys
from isaacsim.core.api import World
from isaacsim.core.utils.stage import add_reference_to_stage
from pathlib import Path

from lightings import setup_lighting
from conveyor_setup import collect_track_details_from_stage, TrackType
from track_operator_task import TrackOperatorTask
from box_supplier_task import BoxSupplierTask
from physics_actions import set_surface_velocity

current_dir = Path(__file__).parent
asset_root_path = str(current_dir / "assets")

world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()
setup_lighting()

# get conveyor track details
track_asset = str(Path(asset_root_path) / "conveyor_room.usd")
add_reference_to_stage(usd_path=track_asset, prim_path="/World")
tracks = collect_track_details_from_stage("/World")
track_directions = [1, 1, 1, -1] # its temporary fix, while setting usd this should be taken care.

# add task to produce boxes to be transferred
supplier_task = BoxSupplierTask()
world.add_task(supplier_task)

# create track operators and also set initial velocity for each tracj
initial_velocity = 0.5
track_operator_names = []
for index, (track_path, properties) in enumerate(tracks.items()):
    # task that manages movement of box at a junction
    if properties[0] == TrackType.CROSS:
        task_name = f"track_operaotr_task_{index}" 
        track_operator_task = TrackOperatorTask(properties[1], name=task_name)
        world.add_task(track_operator_task)
        track_operator_names.append(task_name)
    set_surface_velocity(properties[1], initial_velocity * track_directions[index])


world.reset()
world.play()

step_count = 0
switch_frequency = 3 # switches every (4-1) boxes
switch_event = False

while simulation_app.is_running():

    switch_event = supplier_task.get_observations()["box_crossed"] % switch_frequency == 0
    if switch_event:
        for name in track_operator_names:
            if (task := world.get_task(name)) is not None:
                switch = task.toggle_cross_switch()
                if switch == True:
                    print("belt is doing cross transfer for each item")
                else:
                    print("belt is doing straight transfer for each item")

    # advance the  world
    world.step(render=True)
    step_count += 1

simulation_app.close()
