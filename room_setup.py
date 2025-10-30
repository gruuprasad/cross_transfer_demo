from isaacsim.core.utils.stage import add_reference_to_stage
from pathlib import Path

from lightings import setup_lighting
from sensors import setup_contact_sensor
from tracks_controller import ConveyorTracksController

import carb

package_base_path = Path(__file__).parent
asset_root_path = str(package_base_path / "assets")

class ConveyorRoom:
    def __init__(self, world):
        carb.log_info("creating the room...")
        self._world = world
        self._box_dropoff_point = [-2.0, 0.0, 1.0]
        self._box_scale = [0.2, 0.2, 0.2]
        self._contact_sensor = None
        self._initialized = False

        self.setup_room()

    def setup_room(self):
        carb.log_info("setup_room():")

        setup_lighting()

        # Conveyor tracks
        # USD contains prebuilt scene (using conveyor builder plugin) containing conveyor track layout.
        track_asset = str(Path(asset_root_path) / "conveyor_track_setup.usd")
        add_reference_to_stage(usd_path=track_asset, prim_path="/World/Tracks")
        self.tracks_controller = ConveyorTracksController(prefix_path="/World/Tracks")

        self._contact_sensor = setup_contact_sensor()

        carb.log_info("setup_scene():exiting")

    def update(self):
        if not self._initialized:
            # Things to set before first tick
            self.tracks_controller.set_all_surface_velocities([1.0, 0.0, 0.0])
            self._initialized = True

        self._world.step(render=True)
