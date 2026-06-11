from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform, PERCENTAGE, UnitOfTime

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.COVER: {
                "updown": {
                    "open_value": "up",
                    "close_value": "down",
                    "stop_value": "pause",
                }
            },
            Platform.NUMBER: {
                "custom_height": {
                    "min": 0,
                    "max": 100,
                    "step": 10,
                },
                "custom_timing": {
                    "min": 0,
                    "max": 180,
                    "step": 5,
                    "unit_of_measurement": UnitOfTime.MINUTES
                }
            },
            Platform.LIGHT: {
                "common_light": {
                    "power": "light",
                    "brightness": {"light_brightness": [20, 100]}
                }
            },
            Platform.SWITCH: {
                "laundry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "offline_voice_function": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            }
        }
    },
    "default_laundry_rack": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.COVER: {
                "updown": {
                    "open_value": "up",
                    "close_value": "down",
                    "stop_value": "pause",
                }
            },
            Platform.NUMBER: {
                "custom_height": {
                    "min": 0,
                    "max": 100,
                    "step": 10,
                    "translation_key": "laundry_height",
                },
                "custom_timing": {
                    "min": 0,
                    "max": 180,
                    "step": 5,
                    "unit_of_measurement": UnitOfTime.MINUTES
                }
            },
            Platform.LIGHT: {
                "common_light": {
                    "power": "light",
                    "brightness": {"light_brightness": [20, 100]}
                }
            },
            Platform.SWITCH: {
                "laundry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "offline_voice_function": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            }
        }
    }
}
