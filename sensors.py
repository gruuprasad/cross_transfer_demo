from isaacsim.sensors.physics import ContactSensor

import carb

parent_prim = "/World/TrackArea/sensor_base_01"
sensor_name = "sensor1"

def setup_contact_sensor():
    try:
        prim_path = parent_prim + "/" + sensor_name
        sensor = ContactSensor(
            prim_path=prim_path,
            name=sensor_name,
            frequency=60
        )
    except Exception as e:
        carb.log_error(f"setup_contact_sensor():failed"
                        "to create sensor at {prim_path} with error:{e}")
    return sensor
