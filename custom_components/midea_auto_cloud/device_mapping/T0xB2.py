from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "work_status", "work_mode", "lock", "furnace_light", 
            "dissipate_heat", "pre_heat", "door_open", "lack_water"
        ],
        "entities": {
            Platform.BINARY_SENSOR: {
                "lock": {
                    "device_class": BinarySensorDeviceClass.LOCK,
                },
                "furnace_light": {
                    "device_class": BinarySensorDeviceClass.LIGHT,
                },
                "dissipate_heat": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "pre_heat": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "door_open": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "lack_water": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "high_temperature_work": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "lack_box": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "clean_sink_ponding": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "clean_scale": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "flip_side": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "reaction": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "ramadan": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "change_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "execute": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                }
            },
            Platform.SELECT: {
                "work_status": {
                    "options": {
                        "standby": {"work_status": "standby"},
                        "working": {"work_status": "working"},
                        "pause": {"work_status": "pause"},
                        "finish": {"work_status": "finish"},
                        "error": {"work_status": "error"}
                    }
                },
                "work_mode": {
                    "options": {
                        "off": {"work_mode": "0"},
                        "steam": {"work_mode": "1"},
                        "cook": {"work_mode": "2"},
                        "fry": {"work_mode": "3"},
                        "bake": {"work_mode": "4"},
                        "roast": {"work_mode": "5"},
                        "stew": {"work_mode": "6"},
                        "soup": {"work_mode": "7"},
                        "rice": {"work_mode": "8"},
                        "porridge": {"work_mode": "9"},
                        "yogurt": {"work_mode": "10"},
                        "ferment": {"work_mode": "11"},
                        "defrost": {"work_mode": "12"},
                        "keep_warm": {"work_mode": "13"},
                        "clean": {"work_mode": "14"},
                        "custom": {"work_mode": "ff"}
                    }
                }
            },
            Platform.SENSOR: {
                "work_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "work_minute": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "work_second": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
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
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "weight": {
                    "device_class": SensorDeviceClass.WEIGHT,
                    "unit_of_measurement": "g",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "people_number": {
                    "device_class": SensorDeviceClass.DATA_RATE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "steam_quantity": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "totalstep": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "stepnum": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "hour_set": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "minute_set": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "second_set": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "ota": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "version": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cbs_version": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloudmenuid": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
