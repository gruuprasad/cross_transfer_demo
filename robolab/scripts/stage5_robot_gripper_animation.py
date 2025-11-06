from pxr import Usd, UsdGeom, Gf
from utils.scene_utils import get_usd_path

def animate_gripper(stage, robot_index=1):
    """Animate gripper open/close for a given robot."""
    base_path = f"/Lab/Robot_Station_{robot_index}/RobotInstance"
    left_path  = f"{base_path}/Gripper/LeftFinger"
    right_path = f"{base_path}/Gripper/RightFinger"

    left_prim  = stage.GetPrimAtPath(left_path)
    right_prim = stage.GetPrimAtPath(right_path)

    if not (left_prim.IsValid() and right_prim.IsValid()):
        raise RuntimeError(f"❌ Gripper fingers not found for {base_path}")

    left_xf  = UsdGeom.Xformable(left_prim)
    right_xf = UsdGeom.Xformable(right_prim)

    # Create transform ops
    left_op  = left_xf.AddTransformOp() if not left_xf.GetOrderedXformOps() else left_xf.GetOrderedXformOps()[0]
    right_op = right_xf.AddTransformOp() if not right_xf.GetOrderedXformOps() else right_xf.GetOrderedXformOps()[0]

    # Animate translation along X-axis (open → close → open)
    for frame, offset in [(1, 0.0), (12, 0.05), (24, 0.0), (36, 0.05), (48, 0.0)]:
        left_mat  = Gf.Matrix4d().SetTranslate(Gf.Vec3d(-0.15 - offset, 0, 0))
        right_mat = Gf.Matrix4d().SetTranslate(Gf.Vec3d( 0.15 + offset, 0, 0))
        left_op.Set(left_mat,  time=frame)
        right_op.Set(right_mat, time=frame)

def main():
    lab_path = get_usd_path("scenes", "RobotLab.usda")
    stage = Usd.Stage.Open(lab_path)
    if not stage:
        raise RuntimeError("Could not open RobotLab.usda")

    animate_gripper(stage, robot_index=1)

    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(48)
    stage.GetRootLayer().Save()
    print("✅ Added gripper open/close animation to Robot_Station_1")

if __name__ == "__main__":
    main()
