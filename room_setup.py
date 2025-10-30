from isaacsim.core.utils.stage import add_reference_to_stage
from pathlib import Path

from lightings import setup_lighting

package_base_path = Path(__file__).parent
asset_root_path = str(package_base_path / "assets")

class ConveyorRoom:
    def __init__(self, world):
        print("creating the room...")
        self._world = world
        self._box_dropoff_point = [2.5, 0.0, 1.0]
        self.setup_room()
        self.simulation_ready()

    def setup_room(self):
        print("setup_room():")
        setup_lighting()

        # Conveyor tracks
        # USD contains prebuilt scene (using conveyor builder plugin) containing conveyor track layout.
        track_asset = str(Path(asset_root_path) / "conveyor_room.usd")
        add_reference_to_stage(usd_path=track_asset, prim_path="/World/TrackArea")
        print("setup_scene():exiting")

    def simulation_ready(self):
        self._world.reset()
        self._world.play()

    def update(self):
        self._world.step(render=True)
