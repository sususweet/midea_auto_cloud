from copy import deepcopy

from homeassistant.const import Platform, UnitOfTime, UnitOfArea, UnitOfTemperature
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

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

GR6_PRO_MAPPING = deepcopy(DEVICE_MAPPING["default"])
GR6_PRO_MAPPING["calculate"]["set"] = [
    {"lvalue": "[work_minute]", "rvalue": "[work_second] // 60"},
    {"lvalue": "[work_second]", "rvalue": "[work_second] % 60"},
]
GR6_PRO_MAPPING["entities"].update({
    Platform.NUMBER: {
        "gr6_microwave_seconds": {
            "translation_key": "microwave_duration",
            "min": 5,
            "max": 1795,
            "step": 5,
            "mode": "box",
            "unit_of_measurement": UnitOfTime.SECONDS,
            "default_value": None,
        },
    },
    Platform.SELECT: {
        "gr6_microwave_power": {
            "translation_key": "microwave_power",
            "default_value": None,
            "options": {
                "low": {"gr6_microwave_power": "fire_power_1"},
                "medium_low": {"gr6_microwave_power": "fire_power_3"},
                "medium": {"gr6_microwave_power": "fire_power_5"},
                "medium_high": {"gr6_microwave_power": "fire_power_8"},
                "high": {"gr6_microwave_power": "fire_power_10"},
            },
        },
    },
    Platform.BUTTON: {
        "gr6_start_microwave": {
            "translation_key": "start_microwave",
            "command": {
                "work_mode": "microwave_1",
                "work_hour": 0,
                "pre_heat": "off",
            },
            "include_current": {
                "work_second": "gr6_microwave_seconds",
                "fire_power": "gr6_microwave_power",
            },
            "control": {
                "device": {"subtype": ["5"]},
                "parameters": {
                    "work_second": {"min": 5, "max": 1795, "step": 5},
                    "fire_power": {
                        "values": [
                            "fire_power_1", "fire_power_3", "fire_power_5",
                            "fire_power_8", "fire_power_10",
                        ],
                    },
                },
                "require": {
                    "work_status": ["standby", "save_power", "work_finish"],
                    "door_open": ["off"],
                    "lock": ["off"],
                    "error_code": [0, "0"],
                },
                "confirm": {
                    "execute": ["ok"],
                    "work_status": ["work", "work_finish"],
                    "work_mode": ["microwave_1"],
                },
            },
        },
        "gr6_pause": {
            "translation_key": "pause_cooking",
            "command": {"work_status": "pause"},
            "control": {
                "device": {"subtype": ["5"]},
                "require": {"work_status": ["work"]},
                "confirm": {
                    "execute": ["ok"],
                    "work_status": ["pause", "pause_c"],
                },
            },
        },
        "gr6_resume": {
            "translation_key": "resume_cooking",
            "command": {"work_status": "work"},
            "control": {
                "device": {"subtype": ["5"]},
                "require": {
                    "work_status": ["pause", "pause_c"],
                    "door_open": ["off"],
                    "lock": ["off"],
                    "error_code": [0, "0"],
                },
                "confirm": {
                    "execute": ["ok"],
                    "work_status": ["work", "work_finish"],
                },
            },
        },
        "gr6_cancel": {
            "translation_key": "cancel_cooking",
            "command": {"work_status": "standby"},
            "control": {
                "device": {"subtype": ["5"]},
                "require": {
                    "work_status": ["work", "pause", "pause_c", "order"],
                },
                "confirm": {
                    "execute": ["ok"],
                    "work_status": ["standby", "save_power", "work_finish"],
                },
            },
        },
    },
})
DEVICE_MAPPING["700006DJ"] = GR6_PRO_MAPPING
