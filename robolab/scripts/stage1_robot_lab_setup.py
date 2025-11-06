# stage1_robot_lab_setup.py
from pxr import Sdf, Usd, UsdGeom, Gf

from utils.scene_utils import ensure_folder_structure, get_usd_path

ensure_folder_structure()

# ------------------------------------------------------------
# 1️⃣  Create a new USD stage
# ------------------------------------------------------------
stage_path = get_usd_path("scenes", "RobotLab.usda")
stage = Usd.Stage.CreateNew(stage_path)
stage.SetMetadata("comment", "Stage 1 - Robot Lab basic environment")
stage.SetMetadata("upAxis", "Y")
stage.SetMetadata("metersPerUnit", 1.0)

# ------------------------------------------------------------
# 2️⃣  Create a root Xform for the lab
# ------------------------------------------------------------
lab = UsdGeom.Xform.Define(stage, "/Lab")

# Add a simple custom attribute (metadata-style)
lab_prim = lab.GetPrim()
lab_prim.CreateAttribute("lab:temperature", Sdf.ValueTypeNames.Float).Set(22.5)
lab_prim.CreateAttribute("lab:powerStatus", Sdf.ValueTypeNames.Token).Set("online")

# ------------------------------------------------------------
# 3️⃣  Add a floor (a scaled cube)
# ------------------------------------------------------------
floor = UsdGeom.Cube.Define(stage, "/Lab/Floor")
floor.AddTranslateOp().Set(Gf.Vec3f(0, -0.5, 0))
floor.AddScaleOp().Set(Gf.Vec3f(10, 1, 10))  # 10×10 m floor

# ------------------------------------------------------------
# 4️⃣  Create placeholder stations for robots
# ------------------------------------------------------------
num_stations = 3
spacing = 4.0
for i in range(num_stations):
    station_path = f"/Lab/Robot_Station_{i+1}"
    station = UsdGeom.Xform.Define(stage, station_path)
    # spread them out along X axis
    station.AddTranslateOp().Set(Gf.Vec3f(i * spacing - spacing, 0, 0))

    # a simple visual marker for the station
    marker = UsdGeom.Cylinder.Define(stage, station_path + "/Marker")
    marker.AddScaleOp().Set(Gf.Vec3f(0.5, 0.1, 0.5))
    marker.AddTranslateOp().Set(Gf.Vec3f(0, 0.1, 0))

# ------------------------------------------------------------
# 5️⃣  Add a light (optional, helps in usdview)
# ------------------------------------------------------------
light = UsdGeom.Sphere.Define(stage, "/Lab/LightProxy")
light.AddTranslateOp().Set(Gf.Vec3f(0, 5, 0))
light.AddScaleOp().Set(Gf.Vec3f(0.2))
# (Later you could replace this with a real UsdLux light.)

# ------------------------------------------------------------
# 6️⃣  Save the stage
# ------------------------------------------------------------
stage.GetRootLayer().Save()
print("✅  RobotLab.usda created. Open it in usdview to explore.")
