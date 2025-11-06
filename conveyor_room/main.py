from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

from isaacsim.core.utils.extensions import enable_extension
enable_extension("isaacsim.asset.gen.conveyor")

from isaacsim.core.api import World
from isaacsim.core.utils.stage import add_reference_to_stage
from pathlib import Path

from scene_setup.lightings import setup_lighting
from scene_setup.conveyor_setup import read_track_details 
from tasks.box_supplier_task import BoxSupplierTask
from tasks.track_supervisor_task import TrackSupervisorTask

current_dir = Path(__file__).parent
asset_root_path = str(current_dir / "assets")

world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()
setup_lighting()

# get conveyor track details
track_asset = str(Path(asset_root_path) / "conveyor_room.usd")
add_reference_to_stage(usd_path=track_asset, prim_path="/World")
tracks = read_track_details("/World")

# add task to produce boxes to be transferred
supplier_task = BoxSupplierTask()
world.add_task(supplier_task)

supervisor_task = TrackSupervisorTask(tracks)
world.add_task(supervisor_task)

world.reset()
world.play()

while simulation_app.is_running():
    world.step(render=True)

simulation_app.close()
