from isaacsim.core.api.tasks import BaseTask
import omni.usd

from enum import Enum

from common.math_utils import hadamard_product
from common.types import TrackState
from physics.surface_velocity import set_surface_velocity_direction
from scene_setup.sensors import setup_contact_sensor

class TrackOperatorTask(BaseTask):
    """
    this task performs either straight or cross transfer based on input. 
    internally uses the sensor reading to manage the track state.
    """
    def __init__(self, track_info, name="track_operator_task"):  
        super().__init__(name=name)
        self._contact_sensor = None
        self._track_info = track_info
        self._track_state = TrackState.STRAIGHT
        self._cross_switch = False
        self._item_present = False

        # Debounce variables
        self._contact_counter = 0
        self._debounced_item_present = False
        self._last_raw_contact = False

        # Thresholds
        self._contact_on_threshold = 5  # frames required to confirm contact
        self._contact_off_threshold = 3  # frames required to confirm loss of contact

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        # read these things from config
        self._contact_sensor_prim_path = "/World/sensor_base_01/Contact_Sensor" #TODO: read from config
        self._contact_sensor = setup_contact_sensor(self._contact_sensor_prim_path)

    def get_observations(self):
        observations = {
            "track_state": self._track_state,
            "item_present": self._debounced_item_present
        }
        return observations

    def _update_debounced_contact(self):
        raw_contact = self._contact_sensor.get_current_frame()["in_contact"]

        if raw_contact == self._last_raw_contact:
            self._contact_counter += 1
        else:
            self._contact_counter = 1  # reset counter on change
            self._last_raw_contact = raw_contact

        # Apply thresholds
        if raw_contact and self._contact_counter >= self._contact_on_threshold:
            self._debounced_item_present = True
        elif not raw_contact and self._contact_counter >= self._contact_off_threshold:
            self._debounced_item_present = False

        return self._debounced_item_present

    def toggle_cross_switch(self):
        self._cross_switch = not self._cross_switch
        return self._cross_switch

    def pre_step(self, step_index, simulation_time):
        self._item_present = self._update_debounced_contact()

        if self._item_present and self._track_state == TrackState.CROSS:
            # wait for item to complete transfer
            return

        if self._item_present and self._cross_switch:
            # set conveyor to move across.
            direction = hadamard_product(self._track_info.direction, [0, 1, 0])
            set_surface_velocity_direction(self._track_info.prim, direction)
            self._track_state = TrackState.CROSS
        elif not self._item_present and self._track_state == TrackState.CROSS:
            # set conveyor to move stright.
            direction = hadamard_product(self._track_info.direction, [1, 0, 0])
            set_surface_velocity_direction(self._track_info.prim, direction)
            self._track_state = TrackState.STRAIGHT
