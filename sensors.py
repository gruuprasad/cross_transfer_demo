from isaacsim.sensors.physics import ContactSensor

sensor_base = "World/sensor_base_01"

def setup_contact_sensor(sensor_prim_name):
    prim_full_path = sensor_base + sensor_prim_name
    sensor = ContactSensor(
        prim_path=prim_full_path,
        name=sensor_prim_name,
        frequency=60
    )
    return sensor
