from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform, PERCENTAGE, UnitOfTime

DEVICE_MAPPING = {
    "default_laundry_rack": {
        "rationale": ["off", "on"],
        "entities": {
            Platform.SELECT: {
                "updown": {
                    "options": {
                        "up": {"updown": "up"},
                        "down": {"updown": "down"},
                        "pause": {"updown": "pause"}
                    },
                }
            },
            Platform.NUMBER: {
                "light_brightness": {
                    "min": 20,
                    "max": 100,
                    "step": 1,
                    "unit_of_measurement": PERCENTAGE,
                    "translation_key": "lightness"
                },
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
            Platform.SWITCH: {
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
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
