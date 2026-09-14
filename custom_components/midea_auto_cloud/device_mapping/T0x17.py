from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
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
    },
    # Midea D35W MAX smart laundry rack (sn8 M1100014), verified against
    # lua protocol T_0000_17_M1100014_2025121306.lua and a real device.
    "M1100014": {
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
                    "unit_of_measurement": UnitOfTime.MINUTES,
                },
                "timing_light_off": {
                    "min": 0,
                    "max": 1440,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                },
                "voice_set": {
                    "min": 0,
                    "max": 100,
                    "step": 1,
                },
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
                },
                "set_light_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "mic_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "horn_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wakeup_free_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "continuous_dialogue_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "remote_control_broadcast_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "lift_up_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wifi_light_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.BINARY_SENSOR: {
                "body_induction": {
                    "device_class": BinarySensorDeviceClass.MOTION,
                },
            },
            Platform.SENSOR: {
                "current_height": {
                    "state_class": SensorStateClass.MEASUREMENT,
                    "unit_of_measurement": "cm",
                },
                "location_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "options": ["normal", "upper_limit", "lower_limit"],
                },
                "error_code": {
                    "state_class": SensorStateClass.MEASUREMENT,
                },
            },
        }
    }
}
