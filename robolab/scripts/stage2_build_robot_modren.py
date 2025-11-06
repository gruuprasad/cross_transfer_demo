from pxr import Sdf, Usd, UsdGeom, Gf
from utils.scene_utils import ensure_folder_structure, get_usd_path


def build_robot_asset():
    # ------------------------------------------------------------
    # 1️⃣  Setup and create stage
    # ------------------------------------------------------------
    ensure_folder_structure()
    stage_path = get_usd_path("assets/robots", "Robot.usda")

    stage = Usd.Stage.CreateNew(stage_path)
    stage.SetMetadata("comment", "Stage 2 - Modular Robot Asset")
    stage.SetMetadata("upAxis", "Y")
    stage.SetMetadata("metersPerUnit", 1.0)

    # ------------------------------------------------------------
    # 2️⃣  Root robot prim
    # ------------------------------------------------------------
    robot = UsdGeom.Xform.Define(stage, "/Robot")
    stage.SetDefaultPrim(robot.GetPrim())
    robot_prim = robot.GetPrim()
    robot_prim.CreateAttribute("robot:serialNumber", Sdf.ValueTypeNames.String).Set("RBT-001")
    robot_prim.CreateAttribute("robot:status", Sdf.ValueTypeNames.Token).Set("idle")

    # ------------------------------------------------------------
    # 3️⃣  Base
    # ------------------------------------------------------------
    base = UsdGeom.Xform.Define(stage, "/Robot/Base")
    base_xform = (
        Gf.Matrix4d().SetScale(Gf.Vec3d(1.5, 0.5, 1.5)) *
        Gf.Matrix4d().SetTranslate(Gf.Vec3d(0.0, 0.25, 0.0))
    )
    UsdGeom.Xformable(base).AddTransformOp().Set(base_xform)

    base_geom = UsdGeom.Cylinder.Define(stage, "/Robot/Base/Body")
    base_geom.GetHeightAttr().Set(0.5)
    base_geom.GetRadiusAttr().Set(0.8)

    # ------------------------------------------------------------
    # 4️⃣  Arm
    # ------------------------------------------------------------
    arm = UsdGeom.Xform.Define(stage, "/Robot/Arm")
    arm_xform = (
        Gf.Matrix4d().SetScale(Gf.Vec3d(0.3, 2.0, 0.3)) *
        Gf.Matrix4d().SetTranslate(Gf.Vec3d(0.0, 0.75, 0.0))
    )
    UsdGeom.Xformable(arm).AddTransformOp().Set(arm_xform)

    arm_geom = UsdGeom.Cylinder.Define(stage, "/Robot/Arm/Body")
    arm_geom.GetHeightAttr().Set(1.0)
    arm_geom.GetRadiusAttr().Set(0.15)

    # ------------------------------------------------------------
    # 5️⃣  Gripper
    # ------------------------------------------------------------
    gripper = UsdGeom.Xform.Define(stage, "/Robot/Gripper")
    gripper_xform = Gf.Matrix4d().SetTranslate(Gf.Vec3d(0.0, 1.75, 0.0))
    UsdGeom.Xformable(gripper).AddTransformOp().Set(gripper_xform)

    left_finger = UsdGeom.Cube.Define(stage, "/Robot/Gripper/LeftFinger")
    left_xform = (
        Gf.Matrix4d().SetScale(Gf.Vec3d(0.1, 0.3, 0.1)) *
        Gf.Matrix4d().SetTranslate(Gf.Vec3d(-0.15, 0.0, 0.0))
    )
    UsdGeom.Xformable(left_finger).AddTransformOp().Set(left_xform)

    right_finger = UsdGeom.Cube.Define(stage, "/Robot/Gripper/RightFinger")
    right_xform = (
        Gf.Matrix4d().SetScale(Gf.Vec3d(0.1, 0.3, 0.1)) *
        Gf.Matrix4d().SetTranslate(Gf.Vec3d(0.15, 0.0, 0.0))
    )
    UsdGeom.Xformable(right_finger).AddTransformOp().Set(right_xform)

    # ------------------------------------------------------------
    # 6️⃣  Save
    # ------------------------------------------------------------
    stage.GetRootLayer().Save()
    print(f"✅ Robot asset saved at {stage_path}")


if __name__ == "__main__":
    build_robot_asset()
