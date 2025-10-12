from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": ["run_mode", "fan_speed", "cooling_temp", "heating_temp", "extflag"],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "run_mode",
                    "hvac_modes": {
                        "off": {"run_mode": "0"},
                        "fan_only": {"run_mode": "1"},
                        "cool": {"run_mode": "2"},
                        "heat": {"run_mode": "3"},
                        "auto": {"run_mode": "4"},
                        "dry": {"run_mode": "5"}
                    },
                    "fan_modes": {
                        "off": {"fan_speed": "0"},
                        "1": {"fan_speed": "1"},
                        "2": {"fan_speed": "2"},
                        "3": {"fan_speed": "3"},
                        "4": {"fan_speed": "4"},
                        "5": {"fan_speed": "5"},
                        "6": {"fan_speed": "6"},
                        "7": {"fan_speed": "7"},
                        "auto": {"fan_speed": "8"}
                    },
                    "preset_modes": {
                        "none": {"extflag": "0"},
                        "electric_heat": {"extflag": "2"},
                        "swing": {"extflag": "4"},
                        "electric_heat_swing": {"extflag": "6"}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "room_temp",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "is_lock_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ['0', '1']
                },
                "is_lock_cool": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ['0', '1']
                },
                "fan_speed_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ['0', '1']
                },
                "is_lock_rc": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ['0', '1']
                },
            },
            Platform.SENSOR: {
                "room_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "precision": PRECISION_HALVES
                },
                "cool_temp_set": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "precision": PRECISION_HALVES
                },
                "heat_temp_set": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "precision": PRECISION_HALVES
                },
            }
        }
    }
}
