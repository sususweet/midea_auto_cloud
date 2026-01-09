from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[time_running]",
                    "rvalue": "[time_running_hr] * 60 + [time_running_min]"
                },
                {
                    "lvalue": "[time_surplus]",
                    "rvalue": "[time_surplus_hr] * 60 + [time_surplus_min]"
                },
            ],
            "set": []
        },
        "entities": {
            Platform.NUMBER: {
                "temperature": {
                    "min": 25,
                    "max": 100,
                    "step": 1,
                },
                "definite_time_hr": {
                    "min": 0,
                    "max": 3,
                    "step": 1,
                },
                "definite_time_min": {
                    "min": 1,
                    "max": 59,
                    "step": 1,
                },
            },
            Platform.SELECT: {
                "fire_level": {
                    "options": {
                        "120W": {"fire_level": "1"},
                        "300W": {"fire_level": "2"},
                        "500W": {"fire_level": "3"},
                        "800W": {"fire_level": "4"},
                        "1200W": {"fire_level": "5"},
                        "1400W": {"fire_level": "6"},
                        "1600W": {"fire_level": "7"},
                        "1800W": {"fire_level": "8"},
                        "2200W": {"fire_level": "9"},
                    }
                },
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
                "time_surplus": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "time_running": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    }
}
