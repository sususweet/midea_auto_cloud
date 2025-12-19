from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform, UnitOfTime, UnitOfArea, UnitOfTemperature
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SELECT:{
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
                    "step": 1
                },
                "custom_height": {
                    "min": 0,
                    "max": 100,
                    "step": 10,
                    "translation_key": "laundry_height",
                }
            },
            Platform.SWITCH: {
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "laundry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
        }
    }
}
