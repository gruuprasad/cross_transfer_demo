from isaacsim.sensors.physics import ContactSensor

parent_prim = "/World/TrackArea/sensor_base_01"
sensor_name = "sensor1"

def setup_contact_sensor():
    prim_path = parent_prim + "/" + sensor_name
    sensor = ContactSensor(
        prim_path=prim_path,
        name=sensor_name,
        frequency=60
    )
    return sensor
