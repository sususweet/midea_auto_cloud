from homeassistant.const import Platform, UnitOfTime, UnitOfArea, UnitOfTemperature
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from ..gr6_pro import add_gr6_pro_mapping

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[work_time]",
                    "rvalue": "[work_second] + 60 * [work_minute] + 3600 * [work_hour]"
                },
                {
                    "lvalue": "[set_time]",
                    "rvalue": "[second_set] + 60 * [minute_set] + 3600 * [hour_set]"
                }
            ],
            "set": [
            ]
        },
        "entities": {
            Platform.BINARY_SENSOR: {
                "clean_scale": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                    "rationale": [0, 1]
                },
                "clean_sink_ponding": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                    "rationale": [0, 1]
                },
                "lack_box": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                    "rationale": [0, 1]
                },
                "dissipate_heat": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "flip_side": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "rationale": [0, 1]
                },
                "high_temperature_work": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "rationale": [0, 1]
                },
                "pre_heat": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "camera_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "live_video_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "lack_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "rationale": [0, 1]
                },
                "door_open": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "change_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "rationale": [0, 1]
                }
            },
            Platform.SENSOR: {
                "error_code": {},
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temperature_above": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temperature_underside": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "fire_power": {},
                "work_mode": {},
                "mouthfeel": {},
                "execute": {},
                "steam_quantity": {},
                "stepnum": {},
                "totalstep": {},
                "people_number": {},
                "weight": {},
                "version": {},
                "cbs_version": {},
                "work_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "cur_temperature_above": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cur_temperature_underside": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "work_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "set_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    }
}

add_gr6_pro_mapping(DEVICE_MAPPING)
