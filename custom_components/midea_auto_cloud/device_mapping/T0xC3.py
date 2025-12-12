from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, \
    CONCENTRATION_PARTS_PER_MILLION
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}, {""}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "Zone1": {
                    "translation_key": "zone1",
                    "power": "zone1_power_state",
                    "hvac_modes": {
                        "off": {"zone1_power_state": "off"},
                        "heat": {"zone1_power_state": "on"},
                    },
                    "target_temperature": "room_temp_set",
                    "current_temperature": "t4",
                    "min_temp": "room_min_set_temp",
                    "max_temp": "room_max_set_temp",
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "DHW": {
                    "translation_key": "dhw",
                    "power": "dhw_power_state",
                    "hvac_modes": {
                        "off": {"dhw_power_state": "off"},
                        "heat": {"dhw_power_state": "on"},
                    },
                    "target_temperature": "dhw_temp_set",
                    "current_temperature": "t4",
                    "min_temp": "dhw_min_set_temp",
                    "max_temp": "dhw_max_set_temp",
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "fastdhw_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "fastdhw_state",
                },
                "forcetbh_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "forcetbh_state",
                },
            },
            Platform.SENSOR: {
                "run_mode_set": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "mode",
                },
                "room_temp_set": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "room_temperature",
                },
                "t4": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "outside_temperature",
                },
                "tank_actual_temp":{
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                }
            }
        }
    },
    "171H120F": {
        "rationale": ["off", "on"],
        "queries": [{}, {""}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "Zone1": {
                    "translation_key": "zone1",
                    "power": "zone1_power_state",
                    "hvac_modes": {
                        "off": {"zone1_power_state": "off"},
                        "heat": {"zone1_power_state": "on"},
                    },
                    "target_temperature": "zone1_temp_set",
                    "min_temp": "zone1_heat_min_set_temp",
                    "max_temp": "zone1_heat_max_set_temp",
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "DHW": {
                    "translation_key": "dhw",
                    "power": "dhw_power_state",
                    "hvac_modes": {
                        "off": {"dhw_power_state": "off"},
                        "heat": {"dhw_power_state": "on"},
                    },
                    "target_temperature": "dhw_temp_set",
                    "current_temperature": "tank_actual_temp",
                    "min_temp": "dhw_min_set_temp",
                    "max_temp": "dhw_max_set_temp",
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "fastdhw_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "fastdhw_state",
                },
                "forcetbh_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "forcetbh_state",
                },
            },
            Platform.SENSOR: {
                "run_mode_set": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "mode",
                },
                "room_temp_set": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "room_temperature",
                },
                "tank_actual_temp":{
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "cur_temperature",
                }
            }
        }
    }
}
