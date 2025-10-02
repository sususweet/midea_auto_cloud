from homeassistant.const import Platform, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power", "ai_switch", "light", "appointment", "prevent_wrinkle_switch",
            "steam_switch", "damp_dry_signal", "eco_dry_switch", "bucket_clean_switch",
            "water_box", "baby_lock", "remind_sound", "steam", "prevent_wrinkle",
            "material", "sterilize", "dryness_level", "dry_temp", "intensity", "program"
        ],
        "entities": {
            Platform.SWITCH: {
                "ai_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "appointment": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "prevent_wrinkle_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "steam_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "damp_dry_signal": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "eco_dry_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "bucket_clean_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_box": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "baby_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "remind_sound": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "steam": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.BINARY_SENSOR: {
                "door_warn": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            },
            Platform.SELECT: {
                "prevent_wrinkle": {
                    "options": {
                        "off": {"prevent_wrinkle": "0"},
                        "low": {"prevent_wrinkle": "1"},
                        "medium": {"prevent_wrinkle": "2"},
                        "high": {"prevent_wrinkle": "3"}
                    }
                },
                "material": {
                    "options": {
                        "cotton": {"material": "0"},
                        "synthetic": {"material": "1"},
                        "wool": {"material": "2"},
                        "delicate": {"material": "3"},
                        "mixed": {"material": "4"}
                    }
                },
                "sterilize": {
                    "options": {
                        "off": {"sterilize": "0"},
                        "on": {"sterilize": "1"}
                    }
                },
                "dryness_level": {
                    "options": {
                        "extra_dry": {"dryness_level": "0"},
                        "dry": {"dryness_level": "1"},
                        "normal": {"dryness_level": "2"},
                        "damp": {"dryness_level": "3"}
                    }
                },
                "dry_temp": {
                    "options": {
                        "low": {"dry_temp": "0"},
                        "medium": {"dry_temp": "1"},
                        "high": {"dry_temp": "2"},
                        "extra_high": {"dry_temp": "3"}
                    }
                },
                "intensity": {
                    "options": {
                        "low": {"intensity": "0"},
                        "medium": {"intensity": "1"},
                        "high": {"intensity": "2"}
                    }
                },
                "program": {
                    "options": {
                        "mixed_wash": {"program": "mixed_wash"},
                        "cotton": {"program": "cotton"},
                        "synthetic": {"program": "synthetic"},
                        "wool": {"program": "wool"},
                        "delicate": {"program": "delicate"},
                        "quick": {"program": "quick"},
                        "eco": {"program": "eco"}
                    }
                }
            },
            Platform.SENSOR: {
                "running_status": {
                    "icon": "mdi:washing-machine"
                },
                "appointment_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "remain_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "progress": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "dry_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
