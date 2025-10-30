from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.api.tasks import BaseTask

import numpy as np

class BoxSupplierTask(BaseTask):
    """
        This class creates boxes and drops it on the conveyor belt.
        box creation interval is controlled.
    """
    def __init__(self, name="box_delivery_task"):  
        print("BoxSupplierTask called")
        super().__init__(name=name)  
        self._boxes = {}  
        self._box_count = 0
        self._starting_pos = [-2.0, 0.0, 1.0]

    def set_up_scene(self, scene):  
        super().set_up_scene(scene)
        print("setup_scene called")
        # Spawn box at the conveyor start location  
        box_name = f"box{self._box_count + 1}"
        box_prim = scene.add(DynamicCuboid(prim_path=f"/World/boxes/{box_name}",
                                      name=box_name,
                                      position=np.array(self._starting_pos),
                                      scale=np.array([0.2, 0.2, 0.2]),
                                      color=np.array([0, 1.0, 0])))
        if box_prim:
            self._boxes[box_name] = box_prim
            self._box_count += 1

    def get_observations():
        return None

    def pre_step(self, step_index, simulation_time):
        """called before stepping the physics simulation.
        """
        pass
