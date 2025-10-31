from isaacsim.core.utils.stage import add_reference_to_stage
from pathlib import Path
import omni.usd

from lightings import setup_lighting
from tracks_controller import ConveyorTracksController
from conveyor_setup import collect_track_details_from_stage

import carb

package_base_path = Path(__file__).parent
asset_root_path = str(package_base_path / "assets")

class ConveyorRoom:
    def __init__(self, world):
        carb.log_info("creating the room...")
        self._world = world
        self._initialized = False
        self._tracks = None

        self.setup_room()

    def setup_room(self):
        carb.log_info("setup_room():")

        setup_lighting()

        # Conveyor tracks
        # USD contains prebuilt scene (using conveyor builder plugin) containing conveyor track layout.
        track_asset = str(Path(asset_root_path) / "conveyor_track_setup.usd")
        add_reference_to_stage(usd_path=track_asset, prim_path="/World/Tracks")
        self.tracks = collect_track_details_from_stage("/World/Tracks")

        # probably track controller won't be needed.
        self.tracks_controller = ConveyorTracksController(self.tracks)
        carb.log_info("setup_scene():exiting")

    def update(self):
        if not self._initialized:
            # Things to set before first tick
            self.tracks_controller.set_all_surface_velocities(0.5)
            self._initialized = True

        self._world.step(render=True)
