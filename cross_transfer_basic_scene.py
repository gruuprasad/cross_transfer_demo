from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

from isaacsim.core.utils.extensions import enable_extension

# Enable Conveyor extension
enable_extension("isaacsim.asset.gen.conveyor")

import sys
from isaacsim.core.api import World
from room_setup import ConveyorRoom

world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

# sets the scene and make it simulation ready
conveyor_room = ConveyorRoom(world)

step_count = 0
while simulation_app.is_running():

    # advance the  world
    conveyor_room.update()
    step_count += 1

simulation_app.close()
