#from isaacsim.sensors.physics import ContactSensor
import omni.kit.commands
from pxr import Gf
from isaacsim.sensors.physics import _sensor

sensor_path = "/World/sensor_base_01/Contact_Sensor"

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
    # try:
    #     success, sensor_prim = omni.kit.commands.execute(
    #         "IsaacSensorCreateContactSensor",
    #         path="Contact_Sensor",
    #         parent=sensor_base,
    #         sensor_period=1,
    #         min_threshold=0.0001,
    #         max_threshold=100000,
    #         translation = Gf.Vec3d(0, 0, 0),
    #     )
    #         #
    #         # prim_full_path = sensor_base + sensor_prim_name
    #         # sensor = ContactSensor(
    # #     prim_path=prim_full_path,
    # #     name=sensor_prim_name,
    # #     frequency=60
    # # )
    # except Exception as e:
    #     print(f"sensor creation failed with exception {e}")
    #
    sensor = ContactSensor(sensor_prim_path)
    return sensor
