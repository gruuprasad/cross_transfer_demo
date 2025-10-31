from isaacsim.sensors.physics import ContactSensor

#NOTE: static collision body is placed in the middle
# of coveyor belt junction. Sensor is placed on that patch.
# TODO: To explore how real contact sensros are rigged.
parent_prim = "/World/TrackArea/sensor_base_01"
sensor_name = "sensor1"

def setup_contact_sensor():
    # Define the sensor prim path
    prim_path = f"{parent_prim}/{sensor_name}"
    sensor = ContactSensor(
        prim_path=prim_path,
        name=sensor_name,
        frequency=60
    )

    if sensor:
        return sensor
    print("failed to create sensor")
    return None
