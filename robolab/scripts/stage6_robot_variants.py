# Use this replacement for your stage6 script (or drop it into a helpers file).
from pxr import Usd, UsdGeom, Gf
from utils.scene_utils import get_usd_path

def create_robot_variants(stage, robot_index=1):
    """
    Create 'State' variantSet with 'Idle' and 'Active' variants on robot instance.
    Writes opinions into the variant-edit layer using OverridePrim so they do not
    end up as stronger local opinions.
    """
    robot_path = f"/Lab/Robot_Station_{robot_index}/RobotInstance"
    robot_prim = stage.GetPrimAtPath(robot_path)
    if not robot_prim.IsValid():
        raise RuntimeError(f"❌ Robot instance not found at {robot_path}")

    # Create or get the variant set on this prim
    variant_set = robot_prim.GetVariantSets().AddVariantSet("State")

    # --- IDLE variant ---
    variant_set.AddVariant("Idle")
    variant_set.SetVariantSelection("Idle")

    # Enter the variant edit context. This sets the stage edit target to the variant's layer.
    with variant_set.GetVariantEditContext():
        # Use OverridePrim so we author prim/attrs into the current edit target (the variant layer)
        arm_path = f"{robot_path}/Arm"
        left_path = f"{robot_path}/Gripper/LeftFinger"
        right_path = f"{robot_path}/Gripper/RightFinger"

        # Ensure prim specs exist in the variant layer (OverridePrim creates a prim in edit target)
        arm_prim_variant = stage.OverridePrim(arm_path)
        left_prim_variant = stage.OverridePrim(left_path)
        right_prim_variant = stage.OverridePrim(right_path)

        # Use Xformable wrapper and set or reuse xform op inside variant layer
        arm_xform = UsdGeom.Xformable(arm_prim_variant)
        arm_ops = arm_xform.GetOrderedXformOps()
        if arm_ops:
            arm_ops[0].Set(Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1,0,0), 0)))
        else:
            arm_xform.AddTransformOp().Set(Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1,0,0), 0)))

        for prim_variant, offset in ((left_prim_variant, -0.20), (right_prim_variant, 0.20)):
            xf = UsdGeom.Xformable(prim_variant)
            ops = xf.GetOrderedXformOps()
            mat = Gf.Matrix4d().SetTranslate(Gf.Vec3d(offset, 0, 0))
            if ops:
                ops[0].Set(mat)
            else:
                xf.AddTransformOp().Set(mat)

    # --- ACTIVE variant ---
    variant_set.AddVariant("Active")
    variant_set.SetVariantSelection("Active")

    with variant_set.GetVariantEditContext():
        arm_path = f"{robot_path}/Arm"
        left_path = f"{robot_path}/Gripper/LeftFinger"
        right_path = f"{robot_path}/Gripper/RightFinger"

        arm_prim_variant = stage.OverridePrim(arm_path)
        left_prim_variant = stage.OverridePrim(left_path)
        right_prim_variant = stage.OverridePrim(right_path)

        arm_xform = UsdGeom.Xformable(arm_prim_variant)
        arm_ops = arm_xform.GetOrderedXformOps()
        # arm raised by 75 degrees
        rot_mat = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1,0,0), 75))
        if arm_ops:
            arm_ops[0].Set(rot_mat)
        else:
            arm_xform.AddTransformOp().Set(rot_mat)

        for prim_variant, offset in ((left_prim_variant, -0.10), (right_prim_variant, 0.10)):
            xf = UsdGeom.Xformable(prim_variant)
            ops = xf.GetOrderedXformOps()
            mat = Gf.Matrix4d().SetTranslate(Gf.Vec3d(offset, 0, 0))
            if ops:
                ops[0].Set(mat)
            else:
                xf.AddTransformOp().Set(mat)

    # Set default selection to Idle at the prim-level (optional)
    variant_set.SetVariantSelection("Idle")
    print(f"✅ Added variantSet 'State' to {robot_path}")

def main():
    lab_path = get_usd_path("scenes", "RobotLab.usda")
    stage = Usd.Stage.Open(lab_path)
    if not stage:
        raise RuntimeError("❌ Could not open RobotLab.usda")

    create_robot_variants(stage, robot_index=1)

    arm = stage.GetPrimAtPath("/Lab/Robot_Station_1/RobotInstance/Arm")
    print(arm.GetPrimStack())

    stage.GetRootLayer().Save()

if __name__ == "__main__":
    main()
