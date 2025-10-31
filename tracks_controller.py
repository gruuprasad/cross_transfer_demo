import omni
import omni.usd
from pxr import Gf, PhysxSchema

import carb

class ConveyorTracksController:
    """
    handles setting direction and speed for each conveyor track. it is low level and doesn't handle the behavior logic. 
    1. tracks, involving cross transfer, are driven using physxsurfacevelocityapi schema.
    2. tracks that only move in one direction during operation are driven by omnigraph nodes (because of the simplicity of the existing omnigraph nodes).
    nothing stops one from choosing either one of the methods for all tracks!
    """
    def __init__(self, tracks):
        self._stage = omni.usd.get_context().get_stage()
        self._tracks = tracks
        self._graphs = {} # key:track_path value:graph_prim
        self._conveyor_prims = {} # key: track_path value:conveyor_prim
        self._cross_prim = None # hacky: temporary, remove this

        for track in self._tracks:
            rigid_prim = self._find_rigid_prim_for_conveyor_belt_node(track)
            if rigid_prim is None:
                print(f"There is no roller or sorter body for track {track_path}")
                continue

            track_path = track.GetPath().pathString
            self._conveyor_prims[track_path] = rigid_prim

        # FIXME: Issue: omnigraph has read_speed which is setting the
        # speed value to 0 on each tick. I need to disable that input inorder
        # for driving through omnigraph to work. ATM, driving the belt directly
        # using surface velocity API.
        #self.create_graphs_for_tracks()

    def _create_action_graph(self, graph_name, conveyor_rigid_prim):
        carb.log_info(f"create_action_graph=({conveyor_rigid_prim})")
        result, graph_prim = omni.kit.commands.execute(
            "CreateConveyorBelt",
            prim_name=graph_name,
            conveyor_prim=conveyor_rigid_prim
        )
        if graph_prim is None:
            carb.log_error(f"Failed to create graph {graph_name}")
            return None

        try:
            dir_attr = graph_prim.GetAttribute("inputs:direction")
            dir_attr.Set(Gf.Vec3f(*[1.0, 0.0, 0.0])) # move along +x axis
            attr = graph_prim.GetAttribute("inputs:velocity")
            attr.Set(1.0) # keep the conveyor belt at rest.
        except Exception as e:
            carb.log_error(f"Failed to set node attributes:{e}")
            return None
        carb.log_info(f"create_action_graph-{graph_name}: Success")
        return graph_prim


    def create_graphs_for_tracks(self):
        """
        create omnigraph for each track containing
        three nodes: onTick, conveyorBelt, velocity, direction.
        """
        for track in self._tracks:
            track_path = track.GetPath().pathString
            graph_prim_path = f"{track_path}/ConveyorTrackGraph"
            graph_name = "ConveyorTrackGraph"

            # Remove any existing graph to avoid duplicates
            if self._stage.GetPrimAtPath(graph_prim_path).IsValid():
                carb.log_info(f"Replacing existing ActionGraph under {track_path}")
                self._stage.RemovePrim(graph_prim_path)

            conveyor_rigid_prim = self._find_rigid_prim_for_conveyor_belt_node(track)
            if conveyor_rigid_prim is None:
                carb.log_warn(f"There is no roller or sorter material for track {track_path}")
                continue

            # Create the ActionGraph prim
            graph_prim = self._create_action_graph(graph_name, conveyor_rigid_prim)
            if graph_prim:
                self._graphs[track_path] = graph_prim
                carb.log_info(f"Created ActionGraph for {track_path}.")

    def _find_rigid_prim_for_conveyor_belt_node(self, track_prim):
        """Return the target prim path that should be driven by the conveyor node."""
        for child in track_prim.GetChildren():
            name = child.GetName()
            if name == "Rollers":
                print(f"conveyor_prim path - {child.GetPath().pathString}")
                return child
            if name == "Sorter":
                conveyor_prim = child.GetChild("Sorter_physics")
                if conveyor_prim.IsValid():
                    print(f"conveyor_prim path - {conveyor_prim.GetPath().pathString}")
                    self._cross_prim = conveyor_prim # Remove this!!!
                    return conveyor_prim
        return None

    def set_all_velocities(self, value):
        """Set conveyor belt velocity for all tracks that have action graphs."""
        for track_path, graph_prim in self._graphs.items():
            if graph_prim is None or not graph_prim.IsValid():
                carb.log_warn(f"[set_all_velocities] Invalid graph prim for {track_path}")
                continue
            try:
                vel_attr = graph_prim.GetAttribute("inputs:velocity")
                if vel_attr.IsValid():
                    vel_attr.Set(value)
                    carb.log_info(f"Velocity set to {value} for {track_path}")
                else:
                    carb.log_warn(f"No 'inputs:velocity' attribute on {graph_prim.GetPath()}")
            except Exception as e:
                carb.log_error(f"Failed to set velocity for {track_path}: {e}")

    

    def set_track_speed(self, track_path: str, speed: float):
        graph_prim = self._graphs.get(track_path)
        if not graph_prim:
            carb.log_warn(f"No graph registered for {track_path}")
            return False

        vel_attr = graph_prim.GetAttribute("inputs:velocity")
        if not vel_attr.IsValid():
            carb.log_warn(f"No velocity input on {track_path}")
            return False

        vel_attr.Set(speed)
        carb.log_info(f"[{track_path}] speed set to {speed}")
        return True

    def set_all_surface_velocities(self, vel):
        print("set_all_surface_velocities called")
        for conveyor_prim in self._conveyor_prims.values():
            self.set_surface_velocity(conveyor_prim, vel)

    # for now only toggle between x and y axis.
    # TODO: create General API covering more cases.
    def change_surface_velocity_direction(self, conveyor_prim):
        surface_velocity_api = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(conveyor_prim)
        if surface_velocity_api:
            vel = surface_velocity_api.GetSurfaceVelocityAttr().Get()
            vel = [vel[1], vel[0], vel[2]]
            surface_velocity_api.GetSurfaceVelocityEnabledAttr().Set(False);
            surface_velocity_api.GetSurfaceVelocityEnabledAttr().Set(True);
            surface_velocity_api.GetSurfaceVelocityAttr().Set(Gf.Vec3f(*vel))

    def set_surface_velocity(self, conveyor_prim, vel, axis=0):
        if not (0 <= axis <= 2):
            raise ValueError("axis must be 0 (X), 1 (Y), or 2 (Z)")

        surface_velocity_api = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(conveyor_prim)
        if surface_velocity_api:
        # Get current velocity for debugging
            current_velocity = surface_velocity_api.GetSurfaceVelocityAttr().Get()
            print(f"current_velocity = {current_velocity}")
            # NOTE: taken from conveyor node implementation in isaacsim repo.
            # quoting the exact reason: "Cycle the enabled attr to
            #hardwire it to work on first sim" without this belt doesnt give movement.
            new_vel = [0.0, 0.0, 0.0]
            new_vel[axis] = vel
            surface_velocity_api.GetSurfaceVelocityEnabledAttr().Set(False);
            surface_velocity_api.GetSurfaceVelocityEnabledAttr().Set(True);
            surface_velocity_api.GetSurfaceVelocityAttr().Set(Gf.Vec3f(*new_vel))
            print(f"velocity set to {vel}")
        else:
            print("Prim does not have PhysxSurfaceVelocityAPI applied.")

    def set_track_direction(self, track_path: str, direction: tuple[float, float, float]):
        graph_prim = self._graphs.get(track_path)
        if not graph_prim:
            carb.log_warn(f"No graph registered for {track_path}")
            return False

        dir_attr = graph_prim.GetAttribute("inputs:direction")
        if not dir_attr.IsValid():
            carb.log_warn(f"No direction input on {track_path}")
            return False

        dir_attr.Set(Gf.Vec3f(*direction))
        carb.log_info(f"[{track_path}] direction set to {direction}")
        return True

    def get_tracks(self):
        return self._tracks

    def print_all_surface_velocities(self):
        print("get_all_surface_velocities called")
        for conveyor_prim in self._conveyor_prims.values():
            surface_velocity_api = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(conveyor_prim)
            if surface_velocity_api:
                current_velocity = surface_velocity_api.GetSurfaceVelocityAttr().Get()
                print(f"current_velocity = {current_velocity}")


