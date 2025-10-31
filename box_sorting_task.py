from isaacsim.core.api.tasks import BaseTask
import omni.usd

from sensors import setup_contact_sensor
from box_supplier_task import BoxSupplierTask
from physics_actions import rotate_surface_velocity_direction

conveyor_track_group = "/World/Tracks"

class BoxSortingTask(BaseTask):
    """
    This task collects the observation from box supplier and
    then decides which track to send the object to.
    """
    def __init__(self, cross_prim, name="box_sorting_task"):  
        super().__init__(name=name)
        self._box_supply_task = BoxSupplierTask() 
        self._contact_sensor = None
        self._box_crossing = False
        self._cross_prim = cross_prim

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._box_supply_task.set_up_scene(scene)
        self._sensor_prim_path = "/World/ConveyorTrack_02/sensorbase/sensor1"
        self._contact_sensor = setup_contact_sensor()
        # Get current USD stage handle
        # stage = omni.usd.get_context().get_stage()
        # self._contact_sensor = stage.GetPrimAtPath(self._sensor_prim_path)
        # if self._contact_sensor.IsValid():
        #     print("created valid contact sensor")
        # else:
        #     print("sensor prim is invalid, exiting")
        #     return
        #
    def get_observations(self):
        observations = self._box_supply_task.get_observations()
        observations[self._contact_sensor.GetName()] = {
            "in_contact": self._contact_sensor.get_current_frame()["in_contact"]
        }
        return observations

    def pre_step(self, step_index, simulation_time):
        self._box_supply_task.pre_step(step_index, simulation_time)
        
        in_contact = self._contact_sensor.get_current_frame()["in_contact"]

        # Rising edge: box enters sensor region
        if in_contact and not self._box_crossing:
            rotate_surface_velocity_direction(self._cross_prim)  # activate cross transfer
            self._box_crossing = True

        # Falling edge: box leaves sensor region
        elif not in_contact and self._box_crossing:
            rotate_surface_velocity_direction(self._cross_prim)  # activate cross transfer
            self._box_crossing = False

