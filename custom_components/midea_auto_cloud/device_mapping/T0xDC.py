from homeassistant.const import Platform, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default_clothes_dryer": {
        "rationale": ["off", "on"],
        "entities": {
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH
                },
                "control_status": {
                    "rationale": ["pause", "start"]
                },
                "ai_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "sterilize": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "prevent_wrinkle_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
            },
            Platform.BINARY_SENSOR: {
                "door_warn": {
                    "device_class": BinarySensorDeviceClass.OPENING,
                    "translation_key": "door_opened"
                }
            },
            Platform.SELECT: {
                "program": {
                    "options": {
                        "baby_clothes": {"program": "baby_clothes"},
                        "bed_clothes": {"program": "bed_clothes"},
                        "cotton": {"program": "cotton"},
                        "dehumidification": {"program": "dehumidification"},
                        "down_jacket": {"program": "down_jacket"},
                        "fiber": {"program": "fiber"},
                        "fresh_air": {"program": "fresh_air"},
                        "jean": {"program": "jean"},
                        "mixed_wash": {"program": "mixed_wash"},
                        "outdoor": {"program": "outdoor"},
                        "quick_dry_20": {"program": "quick_dry_20"},
                        "shirt": {"program": "shirt"},
                        "sport_clothes": {"program": "sport_clothes"},
                        "towel": {"program": "towel"},
                        "underwear": {"program": "underwear"},
                        "warm_clothes": {"program": "warm_clothes"}
                    }
                },
                "intensity": {
                    "options": {
                        "off": {"intensity": "1"},
                        "10": {"intensity": "2"},
                        "20": {"intensity": "3"},
                        "30": {"intensity": "4"},
                        "40": {"intensity": "5"}
                    }
                }
            },
            Platform.SENSOR: {
                "running_status": {
                    "device_class": SensorDeviceClass.ENUM
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
