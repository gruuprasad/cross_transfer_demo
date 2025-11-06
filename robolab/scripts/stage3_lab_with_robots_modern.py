from pxr import Usd, UsdGeom, Gf, Sdf
from utils.scene_utils import ensure_folder_structure, get_usd_path

def populate_lab_with_robots():
    # ------------------------------------------------------------
    # 1️⃣ Setup paths
    # ------------------------------------------------------------
    ensure_folder_structure()
    lab_path = get_usd_path("scenes", "RobotLab.usda")
    robot_path = get_usd_path("assets/robots", "Robot.usda")

    # Load the existing RobotLab scene
    stage = Usd.Stage.Open(lab_path)
    if not stage:
        raise RuntimeError("RobotLab.usda not found! Run stage1 script first.")

    # ------------------------------------------------------------
    # 2️⃣ Reference the robot into each station
    # ------------------------------------------------------------
    num_stations = 3
    spacing = 4.0

    for i in range(num_stations):
        station_name = f"/Lab/Robot_Station_{i+1}/RobotInstance"
        robot_prim = stage.DefinePrim(station_name, "Xform")

        # Add a reference to the Robot asset
        robot_prim.GetReferences().AddReference(Sdf.Reference(robot_path))

        # Apply local transform so robots don’t overlap
        x_offset = i * spacing - spacing
        transform = Gf.Matrix4d().SetTranslate(Gf.Vec3d(x_offset, 0.0, 0.0))
        UsdGeom.Xformable(robot_prim).AddTransformOp().Set(transform)

    # ------------------------------------------------------------
    # 3️⃣ Save and verify
    # ------------------------------------------------------------
    stage.GetRootLayer().Save()
    print(f"✅  Added {num_stations} robot references to {lab_path}")
    print("   Each /Lab/Robot_Station_n now contains a RobotInstance.")


if __name__ == "__main__":
    populate_lab_with_robots()
