from pxr import Usd, UsdGeom, Gf
from utils.scene_utils import get_usd_path

def get_translate_op(xformable):
    for op in xformable.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            return op
    return None


def write_base_layer(path):
    stage = Usd.Stage.CreateNew(path)
    robot = UsdGeom.Xform.Define(stage, "/Robot")
    xformable = UsdGeom.Xformable(robot)
    # Create a named translate op (optional, but good for clarity)
    translate_op = xformable.AddTranslateOp()
    translate_op.Set(Gf.Vec3d(0, 0, 0))
    stage.GetRootLayer().Save()
    print(f"✅ Wrote Base Layer: {path}")


def write_animation_layer(path):
    stage = Usd.Stage.CreateNew(path)

    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(48)
    stage.SetTimeCodesPerSecond(24)

    robot = UsdGeom.Xform.Define(stage, "/Robot")
    xformable = UsdGeom.Xformable(robot)

    # ✅ Correct way to create a named translate op
    translate_op = xformable.AddXformOp(
        UsdGeom.XformOp.TypeTranslate,
        UsdGeom.XformOp.PrecisionDouble,
        "translate"
    )

    translate_op.Set(Gf.Vec3d(0, 0, 0), time=1)
    translate_op.Set(Gf.Vec3d(5, 0, 0), time=24)
    translate_op.Set(Gf.Vec3d(0, 0, 0), time=48)

    stage.GetRootLayer().Save()
    print(f"🎬 Wrote Animation Layer: {path}")

def write_override_layer(anim_path, override_path):
    # Create a new override layer
    stage = Usd.Stage.CreateNew(override_path)

    # Reference the animation layer so we inherit its prim structure
    root_layer = stage.GetRootLayer()
    root_layer.subLayerPaths.append(anim_path)

    # Now override the robot's translate op
    robot = UsdGeom.Xform.Define(stage, "/Robot")
    xformable = UsdGeom.Xformable(robot)

    # We override the SAME named op that the animation layer used
    translate_op = None
    for op in robot.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            translate_op = op
            break

    if not translate_op:
        raise RuntimeError("No translate op found in animated layer — names must match")

    # Stronger, non-time-sampled value
    translate_op.Set(Gf.Vec3d(10, 0, 0))

    stage.GetRootLayer().Save()
    print(f"🔧 Wrote Override Layer: {override_path}")

def write_composed_scene(base, anim, override, out):
    stage = Usd.Stage.CreateNew(out)
    root = stage.GetRootLayer()

    # Layer stacking order: base < anim < override
    root.subLayerPaths = [base, anim, override]
    stage.GetRootLayer().Save()
    print(f"🏗️  Composed scene written: {out}")

def inspect(out):
    print("\n🔍 Inspecting Composed Result")
    stage = Usd.Stage.Open(out, load=Usd.Stage.LoadAll)
    robot = stage.GetPrimAtPath("/Robot")
    xform = UsdGeom.Xformable(robot)
    translate_op = get_translate_op(xform)

    print("\nLayer Stack (strongest last):")
    for layer in stage.GetLayerStack():
        print("  ", layer.identifier)

    print("\nFinal Composed Translate Values:")
    for t in [1, 24, 48]:
        print(f"  Frame {t}: {translate_op.Get(t)}")

def main():
    base = get_usd_path("examples", "Base.usda")
    anim = get_usd_path("examples", "Animation.usda")
    override = get_usd_path("examples", "Override.usda")
    out = get_usd_path("examples", "LayeredScene.usda")

    write_base_layer(base)
    write_animation_layer(anim)
    write_override_layer(anim, override)  # Pass animation layer, create the override layer
    write_composed_scene(base, anim, override, out)
    inspect(out)

if __name__ == "__main__":
    main()
