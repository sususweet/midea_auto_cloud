from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": ["temperature", "fire_level", "set_work_time_sec", "sub_type", "childLock_flag", "control_mode"],
        "entities": {
            Platform.NUMBER: {
                "temperature": {
                    "min": 25,
                    "max": 100,
                    "step": 1,
                },
                "fire_level": {
                    "min": 0,
                    "max": 100,
                    "step": 1,
                },
                "set_work_time_sec": {
                    "min": 60,
                    "max": 3600 * 3,
                    "step": 60,
                },
            },
            Platform.SELECT: {
                "work_switch": {
                    "options": {
                        "cancel": {"work_switch": "cancel"},
                        "schedule": {"work_switch": "schedule"},
                        "work": {"work_switch": "work"},
                        "pause": {"work_switch": "pause"},
                        "power_off": {"work_switch": "power_off"},
                        "power_on": {"work_switch": "power_on"}
                    }
                },
            },
            Platform.SENSOR: {
                "work_status": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "cur_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "precision": PRECISION_HALVES
                },
                "cur_fire_level": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "cur_step": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "total_step": {
                    "device_class": SensorDeviceClass.ENUM,
                },
            }
        }
    }
}
