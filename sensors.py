from pxr import UsdGeom, UsdPhysics, PhysxSchema
import omni.usd

def setup_sensor_base(base_path="/World/ConveyorTrack_02/sensorbase"):
    stage = omni.usd.get_context().get_stage()

    # Check if prim exists
    base_prim = stage.GetPrimAtPath(base_path)
    if not base_prim.IsValid() or base_prim.GetTypeName() == "":
        # ✅ Force-create as Cube geometry
        base_prim = UsdGeom.Cube.Define(stage, base_path).GetPrim()
        print(f"Created cube at {base_path}")
    else:
        print(f"Found existing prim at {base_path} of type {base_prim.GetTypeName()}")

    # ✅ Apply collision APIs (no rigid body for sensors)
    UsdPhysics.CollisionAPI.Apply(base_prim)
    PhysxSchema.PhysxCollisionAPI.Apply(base_prim)

    # ✅ Enable trigger detection (non-blocking)
    base_prim.GetAttribute("physxCollision:collisionEnabled").Set(True)
    base_prim.GetAttribute("physxCollision:trigger").Set(True)

    # Optional fine-tuning
    base_prim.GetAttribute("physxCollision:contactOffset").Set(0.01)
    base_prim.GetAttribute("physxCollision:restOffset").Set(-0.01)

    # ✅ Transform (center + scale)
    xform_api = UsdGeom.XformCommonAPI(base_prim)
    xform_api.SetTranslate((0.0, 0.0, 0.0))
    xform_api.SetRotate((0.0, 0.0, 0.0))
    xform_api.SetScale((0.2, 0.2, 0.2))

    print(f"✅ Sensor base ready at {base_path}")
    return base_prim

def setup_contact_sensor():
    setup_sensor_base()
    # Create contact sensor
    sensor_path = f"{base_path}/sensor1"
    sensor = ContactSensor(
        prim_path=sensor_path,
        name="sensor1",
        frequency=60
    )
    return sensor

    print(f"✅ Non-blocking contact sensor created at {sensor_path}")
