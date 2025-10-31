from isaacsim.core.api.tasks import BaseTask

from sensors import setup_contact_sensor
from box_supplier_task import BoxSupplierTask

conveyor_track_group = "/World/Tracks"

class BoxSortingTask(BaseTask):
    """
    This task collects the observation from box supplier and
    then decides which track to send the object to.
    """
    def __init__(self, room_prim, name="box_sorting_task"):  
        super().__init__(name=name)
        self._box_supply_task = BoxSupplierTask() 
        self._contact_sensor = None
        self._cross_prim = room_prim.tracks_controller.cross_prim
        self._controller = room_prim.tracks_controller
        self._box_crossing = False

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._box_supply_task.set_up_scene(scene)
        self._contact_sensor = setup_contact_sensor()

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
            self._controller.change_surface_velocity_direction(self._cross_prim)  # activate cross transfer
            self._box_crossing = True

        # Falling edge: box leaves sensor region
        elif not in_contact and self._box_crossing:
            self._controller.change_surface_velocity_direction(self._cross_prim)  # activate cross transfer
            self._box_crossing = False

