from pxr import Usd, UsdGeom, Gf
from utils.scene_utils import get_usd_path

def animate_robot_arm():
    # ------------------------------------------------------------
    # 1️⃣  Open scene
    # ------------------------------------------------------------
    lab_path = get_usd_path("scenes", "RobotLab.usda")
    stage = Usd.Stage.Open(lab_path)
    if not stage:
        raise RuntimeError("❌  Could not open RobotLab.usda. Run Stage 3 first.")

    # ------------------------------------------------------------
    # 2️⃣  Choose which robot to animate
    # ------------------------------------------------------------
    # Let’s animate the first robot instance
    robot_arm_path = "/Lab/Robot_Station_1/RobotInstance/Arm"
    arm_prim = stage.GetPrimAtPath(robot_arm_path)
    if not arm_prim.IsValid():
        raise RuntimeError(f"❌  Arm prim not found at {robot_arm_path}")

    arm_xformable = UsdGeom.Xformable(arm_prim)

    # Get or create the transform op
    ops = arm_xformable.GetOrderedXformOps()
    if ops:
        xform_op = ops[0]
    else:
        xform_op = arm_xformable.AddTransformOp()

    # ------------------------------------------------------------
    # 3️⃣  Animate rotation over time
    # ------------------------------------------------------------
    # We’ll rotate around the X axis from 0° → 90° → 0°
    for frame, angle in [(1, 0), (24, 90), (48, 0)]:
        rotation = Gf.Rotation(Gf.Vec3d(1, 0, 0), angle)
        matrix = Gf.Matrix4d().SetRotate(rotation)
        xform_op.Set(matrix, time=frame)

    # Set start/end time for usdview playback
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(48)

    # ------------------------------------------------------------
    # 4️⃣  Save
    # ------------------------------------------------------------
    stage.GetRootLayer().Save()
    print("✅  Animation added to:", robot_arm_path)
    print("   Scrub timeline in usdview to see motion.")


if __name__ == "__main__":
    animate_robot_arm()
