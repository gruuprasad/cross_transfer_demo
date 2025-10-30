from omni.isaac.core.utils.prims import create_prim

# these things can be stored as JSON config files given by room designer.
# NOTE: Lightings are assuumed to be part of the world, hence hardcoded, they dont change during the operation.
lights = [
    {
        "name": "PointLight",
        "type": "SphereLight",
        "position": (0, 0, 2),
        "attributes": {"intensity": 2000.0, "color": (1.0, 0.9, 0.8), "radius": 0.1},
    },
    {
        "name": "DistantLight",
        "type": "DistantLight",
        "position": (0, 0, 5),
        "attributes": {"intensity": 5000.0, "color": (1.0, 1.0, 1.0), "angle": 0.53},
    },
    {
        "name": "RectLight",
        "type": "RectLight",
        "position": (1.5, 0, 3),
        "attributes": {"intensity": 3000.0, "width": 0.5, "height": 0.5, "color": (1.0, 0.8, 0.6)},
    },
    {
        "name": "DiskLight",
        "type": "DiskLight",
        "position": (-1.5, 0, 3),
        "attributes": {"intensity": 2500.0, "radius": 0.25, "color": (0.9, 0.95, 1.0)},
    },
]


def setup_lighting():
    for light in lights:
        prim_path = f"/World/lights/{light['name']}"
        prim = create_prim(
            prim_path=prim_path,
            prim_type=light["type"],
            translation=light["position"],
        )

        # using "intensity" attribute fails with error no such key, using the usd attribute format.
        #TODO Need to study more on this.
        for attr, value in light["attributes"].items():
            usd_attr_name = f"inputs:{attr}"
            prim.GetAttribute(usd_attr_name).Set(value)
    print("setup_liging::success")
