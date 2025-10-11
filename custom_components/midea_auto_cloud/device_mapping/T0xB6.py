from homeassistant.const import Platform
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wisdom_wind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "wind_pressure": {
                    "options": {
                        "off": {"wind_pressure": "0"},
                        "low": {"wind_pressure": "1"},
                        "medium": {"wind_pressure": "2"},
                        "high": {"wind_pressure": "3"},
                        "extreme": {"wind_pressure": "4"},
                    }
                },
            },
        }
    }
}
