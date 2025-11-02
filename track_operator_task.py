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
        self._item_present = False

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._contact_sensor_prim_path = "/World/sensor_base_01/Contact_Sensor"
        self._contact_sensor = setup_contact_sensor(self._contact_sensor_prim_path)

    def get_observations(self):
        observations = {
            "track_state": self._track_state,
            "item_present": self._contact_sensor.get_current_frame()["in_contact"]
        }
        return observations

    def toggle_cross_switch(self):
        self._cross_switch = not self._cross_switch
        print(f"toggle_cross_switch-{self._cross_switch}")
        return self._cross_switch

    def pre_step(self, step_index, simulation_time):
        self._item_present = self._contact_sensor.get_current_frame()["in_contact"]

        if self._item_present and self._track_state == TrackState.CROSS:
            # wait for item to complete transfer
            print("[track_operator]: doing cross_transfer.")
            return

        if self._item_present and self._cross_switch:
            # set conveyor to move across.
            set_surface_velocity_direction(self._cross_prim, [0, 1, 0])
            print("[track_operator]:called set_surface_velocity_direction:cross")
            self._track_state = TrackState.CROSS
        elif not self._item_present and self._track_state == TrackState.CROSS:
            # set conveyor to move stright.
            set_surface_velocity_direction(self._cross_prim, [-1, 0, 0])
            print("[track_operator]:called set_surface_velocity_direction:straight")
            self._track_state = TrackState.STRAIGHT
