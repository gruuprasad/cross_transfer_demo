Cross-Transfer Conveyor Belt Simulation
==========================================

Overview
--------

This simulation demonstrates a cross-transfer conveyor belt system built using Isaac Sim. The scenario models a material handling system where boxes are continuously spawned onto a conveyor belt network. A special cross-transfer conveyor can dynamically switch between straight-line transport and cross-directional transfer to route boxes between different conveyor paths.

The simulation consists of three main task components working together:

1. **Box Supplier Task**: Continuously generates boxes at regular intervals and places them on the conveyor system
2. **Track Supervisor Task**: Manages the overall conveyor network, initializes track velocities, and controls periodic switching of cross-transfer conveyors
3. **Track Operator Task**: Handles individual cross-transfer conveyor operations, monitoring contact sensors and switching between straight and cross-directional movement

The system uses contact sensors to detect when boxes are present on the cross-transfer conveyor, enabling intelligent switching behavior that prevents interruptions during active transfers.

Running the Demo
----------------

To run the demo:

1. Navigate to your Isaac Sim installation folder
2. Execute the following command:

   .. code-block:: bash

      python.sh <path_to_current_folder>/main.py

**Note**: Tested with Isaac Sim 5.1

Scene Setup
-----------

The scene is configured with the following components:

- **Conveyor Belts**: Created using the ``conveyor_belt_utility`` extension. Conveyor belt prims are equipped with action graphs to control surface velocity of rollers/belts
- **Contact Sensor**: Positioned at the center of the cross-conveyor belt to detect when boxes are present during cross-transfer operations
- **Lighting**: Multiple light sources (SphereLight, DistantLight, RectLight, DiskLight) are configured for proper scene illumination
- **Asset References**: Conveyor room geometry is loaded from USD assets in the ``assets/`` directory

Configuration Variables
-----------------------

The simulation behavior can be customized through ``config/config.json``. Key configuration variables include:

**box_supplier_task**
  - ``box_gap`` (float, default: 0.7): Minimum distance between spawned boxes along the conveyor, measured in meters. Controls the spacing of boxes on the conveyor belt.

**track_supervisor_task**
  - ``switch_interval`` (float, default: 5.0): Time interval in seconds between automatic cross-transfer direction switches. The supervisor task toggles cross-transfer conveyors at this regular interval.

**track_operator_task**
  - ``direction`` (list of 3 floats): Specifies the base direction vector for conveyor movement in [x, y, z] format. Examples:
    - ``[-1, 1, 0]``: Moves left (-x) and forward (+y)
    - ``[1, 1, 0]``: Moves right (+x) and forward (+y)
    - Default direction is ``[1, 1, 0]`` if not specified

Example configuration:

.. code-block:: json

   {
       "box_supplier_task": {
           "box_gap": 0.7
       },
       "track_supervisor_task": {
           "switch_interval": 5.0
       },
       "track_operator_task": {
           "/World/ConveyorTrack_AB_01": {
               "direction": [-1, 1, 0]
           }
       }
   }

Architecture Flow
-----------------

1. **Initialization**: Main script loads conveyor room USD, detects tracks, and sets up lighting
2. **Task Setup**: BoxSupplierTask, TrackSupervisorTask, and TrackOperatorTask instances are created and added to the world
3. **Simulation Loop**:
   - BoxSupplierTask checks spacing and spawns boxes as needed
   - TrackSupervisorTask monitors time and triggers periodic cross-switches
   - TrackOperatorTask reads contact sensors and manages track direction based on:
     * Presence/absence of boxes (via contact sensor)
     * Cross-switch toggle state (from supervisor)
     * Current track state (prevents mid-transfer switches)
4. **Dynamic Control**: Conveyor velocities are updated in real-time using PhysX Surface Velocity API

Next Steps
----------

- Currently only cross conveyor track is operated. Other type of conveyor tracks should be controlled
  to perform smooth operation. 
- Add high-level behavioral logic for more complex routing decisions
- Integrate multiple sensors (e.g., depth cameras, LiDAR) to track object positions during cross-transfer
- Support for more complex conveyor network topologies

This documentation is written with the help of GPT model.
