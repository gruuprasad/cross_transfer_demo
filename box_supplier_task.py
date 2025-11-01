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
    def __init__(self, name="box_supplier_task", goal=100):  
        super().__init__(name=name)  
        self._boxes_goal = goal
        self._box_queue = deque()
        self._box_count = 0
        self._box_crossed
        # some parameters needed for operatiosn, to be queiried from stage,
        # hardcoded for simplicity for now. 
        # Finding the area of placement etc needs identifying the surface region.
        # need to explore the availble options.
        self._starting_pos = [-2.0, 0.0, 0.9]
        self.mid_way = [0.75, 0.0, 0.87]

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self.spawn_box()

    def get_observations(self):
        # send the number of boxes produced so far.
        observations = {
            "box_spawned": self._box_count,
            "box_crossed": self._box_crossed,
            "leading_box": self._box_queue[0],
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

    def pre_step(self, step_index, simulation_time):
        """
            called before stepping the physics simulation.
        """
        if self._box_count >= self._boxes_goal:
            return

        if self._box_queue:
            box_pos, _ = self._box_queue[0].get_world_pose()

            if box_pos[0] >= self.mid_way[0]:
                self._box_crossed += 1
                self.spawn_box()
                self._box_queue.popleft()
