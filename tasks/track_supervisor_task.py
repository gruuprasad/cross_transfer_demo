from isaacsim.core.api.tasks import BaseTask

from common.types import TrackType
from common.math_utils import hadamard_product
from physics.surface_velocity import set_surface_velocity
from tasks.track_operator_task import TrackOperatorTask

class TrackSupervisorTask(BaseTask):
    def __init__(self, tracks, name="track_supervisor_task"):
        super().__init__(name=name)
        self._initialised = False
        self._tracks = tracks
        self._track_tasks = []
        self._track_velocity = [0.8, 0.0, 0.0]
        self._last_switch_time = 0.0      # time (in seconds)
        self._track_switch_interval = 5.0  # every 10 seconds TODO: read from config

        # create task that handles cross-transfers
        for index, (track_path, properties) in enumerate(self._tracks.items()):
            if properties["type"] == TrackType.CROSS:
                task_name = f"track_operator_task_{index}" 
                track_operator_task = TrackOperatorTask(properties["info"], name=task_name)
                self._track_tasks.append(track_operator_task)

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        for task in self._track_tasks:
            task.set_up_scene(scene)

    def pre_step(self, step_index, simulation_time):
        print(f"simulation_time={simulation_time}")
        if not self._initialised:
            # desired direction in which conveyor to be moved
            # during operation, by default its positive coodrinates.
            # it can be set in the config.json.
            for track_data in self._tracks.values():
                direction = track_data["info"].direction
                set_surface_velocity(track_data["info"].prim,
                                 hadamard_product(self._track_velocity, direction))
                print(direction)
            self._initialised = True
            return

        if simulation_time - self._last_switch_time >= self._track_switch_interval:
            for task in self._track_tasks:
                task.toggle_cross_switch()
                self._last_switch_time = simulation_time

        for task in self._track_tasks:
            task.pre_step(step_index, simulation_time)
