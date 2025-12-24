from homeassistant.const import Platform, UnitOfTemperature, UnitOfVolume, UnitOfTime, PERCENTAGE, PRECISION_HALVES, \
    UnitOfEnergy, UnitOfPower
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "screen_close": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["on", "off"],
                }
            },
            Platform.CLIMATE: {
                "electric_heater": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on"}
                    },
                    "target_temperature": "temperature",
                    "current_temperature": "cur_temperature",
                    "min_temp": 5,
                    "max_temp": 35,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SELECT: {
                "gear": {
                    "options": {
                        "low": {"gear": 1},
                        "high": {"gear": 3}
                    }
                }
            },
            Platform.SENSOR: {
                "power_statistics": {
                    "device_class": SensorDeviceClass.POWER,
                    "unit_of_measurement": UnitOfPower.WATT,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
