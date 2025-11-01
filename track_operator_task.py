from isaacsim.core.api.tasks import BaseTask
import omni.usd

from enum import Enum

from sensors import setup_contact_sensor
from physics_actions import set_surface_velocity_direction

class TrackState(Enum):
    STRAIGHT = 0
    CROSS = 1

class TrackOperatorTask(BaseTask):
    """
    This task performs either straight or cross transfer based on input. 
    Internally uses the sensor reading to manage the track state.
    """
    def __init__(self, cross_prim, name="track_operator_task"):  
        super().__init__(name=name)
        self._contact_sensor = None
        self._cross_prim = cross_prim
        self._track_state = TrackState.STRAIGHT
        self._cross_switch = False

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._contact_sensor = setup_contact_sensor()

    def get_observations(self):
        observations = {
            "track_state": self._track_state,
            "item_present": self._contact_sensor.get_current_frame()["in_contact"]    
        }

        return observations

    def toggle_cross_switch(self):
        if self._cross_switch == True:
            self._cross_switch = False
        else:
            self._cross_switch = True
        return self._cross_switch

    def pre_step(self, step_index, simulation_time):
        in_contact = self._contact_sensor.get_current_frame()["in_contact"]
        if in_contact and self._track_state == TrackState.CROSS:
            # wait for item to complete transfer
            return

        if in_contact and self._cross_switch:
            # set conveyor to move cross.
            set_surface_velocity_direction(self._cross_prim, [0, 1, 0])
            self._track_state = TrackState.CROSS
        elif not in_contact and self._track_state == TrackState.CROSS:
            # set conveyor to move stright.
            set_surface_velocity_direction(self._cross_prim, [1, 0, 0])
            self._track_state = TrackState.STRAIGHT
