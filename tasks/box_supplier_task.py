from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.api.tasks import BaseTask

import numpy as np
from collections import deque

class BoxSupplierTask(BaseTask):
    """
        This class creates boxes and drops it on the conveyor belt.
        box creation interval is controlled within this class for now.
        but ideally this is driven outside the Task. From what I understand,
        that's the purpose of this class, where class is container for
        environment asset and provides observation. Controller logic is put
        outside.
    """
    def __init__(self, name="box_supplier_task", goal=1000):  
        super().__init__(name=name)  
        self._running = False
        self._boxes_goal = goal
        self._box_queue = deque()
        self._box_count = 0
        # some parameters needed for operatiosn, to be queiried from stage,
        # hardcoded for simplicity for now. 
        # Finding the area of placement etc needs identifying the surface region.
        # need to explore the availble options.
        self._starting_pos = [-2.0, 0.0, 0.9]

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self.spawn_box()
        self._running = True

    def get_observations(self):
        # send the number of boxes produced so far.
        observations = {
            "box_spawned": self._box_count,
            "queu_length": len(self._box_queue)
        }
        return observations

    def spawn_box(self):
        box_name = f"box{self._box_count + 1}"
        box_prim = self._scene.add(DynamicCuboid(prim_path=f"/World/boxes/{box_name}",
                                                 name=box_name,
                                                 position=np.array(self._starting_pos),
                                                 scale=np.array([0.2, 0.2, 0.2]),
                                                 color=np.array([0, 1.0, 0])))
        if box_prim:
            self._box_queue.append(box_prim)
            self._box_count += 1

    def set_machine_state(state):
        self._running = state

    def pre_step(self, step_index, simulation_time):
        """
            called before stepping the physics simulation.
        """
        if self._running:
            if self._box_queue:
                box_pos, _ = self._box_queue[-1].get_world_pose()
                if (abs(box_pos[0] - self._starting_pos[0])) >= 1.0:
                    self.spawn_box()
            else:
                self.spawn_box()
