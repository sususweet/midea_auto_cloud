from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE, PRECISION_HALVES, PRECISION_WHOLE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "manufacturer": "美的",
        "rationale": ["off", "on"],
        "queries": [{}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[temperature]",
                    "rvalue": "([set_temperature] - 106) / 74 * 37 + 38"
                },
                {
                    "lvalue": "[cur_temperature]",
                    "rvalue": "([water_box_temperature] - 106) / 74 * 37 + 38"
                }
            ],
            "set": [
                {
                    "lvalue": "[set_temperature]",
                    "rvalue": "([temperature] - 38) / 37 * 74 + 106"
                },
            ]
        },
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "water_heater": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on"},
                    },
                    "preset_modes": {
                        "标准": {"mode": "standard"},
                        "节能": {"mode": "energy"},
                        "速热": {"mode": "compatibilizing"},
                    },
                    "target_temperature": "temperature",
                    "current_temperature": "cur_temperature",
                    "min_temp": 38,
                    "max_temp": 75,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_WHOLE,
                }
            },
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "mute": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SENSOR: {
                "cur_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            },
        }
    }
}

