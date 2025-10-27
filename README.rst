To run the demo

- Go to isaacsim installation folder and run:
  
  `python.sh <path_to_current_folder>/cross_transfer_basic_scene.py`

- Tested with Isaacsim 5.1

### Scene setup

- conveyor_belt_utility extension is used to create and position the conveyor belts.
- conveyor_belt prims are equipped with action graph to control the surface velocity of the rollers/belts.
- contact sensor is placed in the centre of the cross-conveyor belt (one that facilitates the cross transfer).
- This demo focuses on using the Isaacsim/Omni APIs to acheive the desired result.

##### Next steps:

- Add high level behavioral logic.
- Add multiple sensors to track the object position during cross-transfer.
- Use other sensors for example depth camera, lidar etc.
- and so on
