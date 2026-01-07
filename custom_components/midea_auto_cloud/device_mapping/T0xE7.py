from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.NUMBER: {
                "temperature": {
                    "min": 25,
                    "max": 100,
                    "step": 1,
                },
                "fire_level": {
                    "min": 120,
                    "max": 2200,
                    "step": 1,
                },
                "set_work_time": {
                    "min": 1,
                    "max": 180,
                    "step": 1,
                },
            },
            Platform.SELECT: {
                "work_status": {
                    "options": {
                        "standby": {"work_status": "0"},
                        "work": {"work_status": "1"},
                        "order": {"work_status": "2"},
                        "keep_warm": {"work_status": "3"},
                        "pause": {"work_status": "4"},
                        "power_off": {"work_status": "5"},
                        "spare_time": {"work_status": "6"},
                    }
                },
            },
            Platform.SENSOR: {
                "work_mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "work_stage": {
                    "device_class": SensorDeviceClass.ENUM,
                },
            }
        }
    }
}
