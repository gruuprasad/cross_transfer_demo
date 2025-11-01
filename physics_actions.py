from pxr import Gf, PhysxSchema

# this function is also redundant
def set_surface_velocity_direction(conveyor_prim, direction):
    if all(axis == 0 for axis in direction):
        print("at least one of the direction axis should be set")
        return

    surface_velocity_api = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(conveyor_prim)
    if surface_velocity_api:
        vel = surface_velocity_api.GetSurfaceVelocityAttr().Get()
        new_vel = [v * d for  v, d in zip(vel, direction)]
        # revisit this toggling action later to decide whether its needed.
        surface_velocity_api.GetSurfaceVelocityEnabledAttr().Set(False);
        surface_velocity_api.GetSurfaceVelocityEnabledAttr().Set(True);
        surface_velocity_api.GetSurfaceVelocityAttr().Set(Gf.Vec3f(*new_vel))

def set_surface_velocity(conveyor_prim, vel, axis=0):
    surface_velocity_api = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(conveyor_prim)
    if surface_velocity_api:
        # Get current velocity for debugging
        current_velocity = surface_velocity_api.GetSurfaceVelocityAttr().Get()
        print(f"current_velocity = {current_velocity}")
        # NOTE: taken from conveyor node implementation in isaacsim repo.
        # quoting the exact reason: "Cycle the enabled attr to
        # hardwire it to work on first sim" without this belt doesnt give movement.
        new_vel = [0.0, 0.0, 0.0]
        new_vel[axis] = vel
        vec = Gf.Vec3f(*new_vel)
        surface_velocity_api.GetSurfaceVelocityEnabledAttr().Set(False);
        surface_velocity_api.GetSurfaceVelocityEnabledAttr().Set(True);
        surface_velocity_api.GetSurfaceVelocityAttr().Set(Gf.Vec3f(vec))
        print(f"velocity set to {vel}")
    else:
        print("Prim does not have PhysxSurfaceVelocityAPI applied.")
