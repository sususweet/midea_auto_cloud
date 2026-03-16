from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default_microwave_oven": {
        "rationale": ["off", "on"],
        "centralized": [
            "work_mode",
            "fire_power",
            "pre_heat",
            "temperature",
            "work_hour",
            "work_minute",
            "work_second",
            "weight"
        ],
        "entities": {
            Platform.SELECT: {
                "work_mode": {
                    "options": {
                        "microwave_1": {"work_mode": "microwave_1"},
                        "double_tube_hot_wind_tube_fan_1": {"work_mode": "double_tube_hot_wind_tube_fan_1"},
                        "steam_double_tube_fan_1": {"work_mode": "steam_double_tube_fan_1"},
                        "double_tube_1": {"work_mode": "double_tube_1"},
                        "steam_double_tube_1": {"work_mode": "steam_double_tube_1"},
                        "fast_unfreeze": {"work_mode": "auto_menu", "cloudmenuid": "217"},
                        "zymosis": {"work_mode": "auto_menu", "cloudmenuid": "997"},
                        "warm": {"work_mode": "auto_menu", "cloudmenuid": "998"},
                        "stop": {"work_status": "standby"},
                        "pause": {"work_status": "pause"},
                        "work": {"work_status": "work"},
                        "none": {"work_mode": "ff"}
                    }
                },
                "fire_power": {
                    "options": {
                        "100": {"fire_power": "high_power"},
                        "80": {"fire_power": "medium_high_power"},
                        "50": {"fire_power": "medium_power"},
                        "30": {"fire_power": "medium_low_power"},
                        "10": {"fire_power": "low_power"},
                        "none": {"fire_power": "ff"}
                    }
                },
                "pre_heat": {
                    "options": {
                        "off": {"pre_heat": "off"},
                        "on": {"pre_heat": "on"}
                    }
                }
            },
            Platform.NUMBER: {
                "temperature": {
                    "min": 0,
                    "max": 250,
                    "step": 5,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS
                },
                "work_hour": {
                    "min": 0,
                    "max": 23,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS
                },
                "work_minute": {
                    "min": 0,
                    "max": 59,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.MINUTES
                },
                "work_second": {
                    "min": 0,
                    "max": 59,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.SECONDS
                },
                "weight": {
                    "min": 0,
                    "max": 1500,
                    "step": 100,
                    "unit_of_measurement": "g"
                }
            },
            Platform.SENSOR: {
                "cur_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "work_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "work_mode": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "fire_power": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                }
            },
            Platform.BINARY_SENSOR: {
                "door_open": {
                    "device_class": BinarySensorDeviceClass.OPENING,
                    "translation_key": "door_opened"
                }
            }
        }
    }
}