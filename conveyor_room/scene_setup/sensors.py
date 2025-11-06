#from isaacsim.sensors.physics import ContactSensor
import omni.kit.commands
from isaacsim.sensors.physics import _sensor

class ContactSensor:
    def __init__(self, sensor_path):
        self._interface = _sensor.acquire_contact_sensor_interface()
        self._sensor_path = sensor_path
        self._current_frame = {}

    def get_current_frame(self):
        sensor_reading = self._interface.get_sensor_reading(self._sensor_path, use_latest_data=True)
        self._current_frame["in_contact"] = bool(sensor_reading.in_contact)
        return self._current_frame

def setup_contact_sensor(sensor_prim_path):
    sensor = ContactSensor(sensor_prim_path)
    if sensor:
        print("sensor setup is completed")
    return sensor
