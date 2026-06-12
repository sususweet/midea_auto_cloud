from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, \
    CONCENTRATION_PARTS_PER_MILLION, UnitOfEnergy
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

# MSC-200D 2N8 pool / spa heat pump (171000AU, subtype 513).
_POOL_HEAT_PUMP_MAPPING = {
    "rationale": ["off", "on"],
    "queries": [{}, {"query_type": 2}],
    "centralized": [],
    "entities": {
        Platform.CLIMATE: {
            "Water": {
                "translation_key": "water",
                "power": "mode",
                "hvac_modes": {
                    "off": {"mode": "off"},
                    "heat": {"mode": "heat"},
                    "cool": {"mode": "cool"},
                    "pump": {"mode": "waterpump"},
                },
                "target_temperature": "set_temperature",
                "current_temperature": "twout_temp",
                "min_temp": "t5s_min",
                "max_temp": "t5s_max",
                "temperature_unit": UnitOfTemperature.CELSIUS,
                "precision": 1,
            }
        },
        Platform.SWITCH: {
            "force_heat": {
                "device_class": SwitchDeviceClass.SWITCH,
                "translation_key": "force_heat",
            },
            "mute_en": {
                "device_class": SwitchDeviceClass.SWITCH,
                "translation_key": "mute_en",
            },
        },
        Platform.SENSOR: {
            "mode": {
                "device_class": SensorDeviceClass.ENUM,
                "translation_key": "mode",
            },
            "set_temperature": {
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
                "translation_key": "set_temperature",
            },
            "twin_temp": {
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
                "translation_key": "inlet_water_temperature",
            },
            "twout_temp": {
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
                "translation_key": "outlet_water_temperature",
            },
            "t4_temp": {
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
                "translation_key": "outside_temperature",
            },
            "total_kwh": {
                "device_class": SensorDeviceClass.ENERGY,
                "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
                "state_class": SensorStateClass.TOTAL_INCREASING,
                "translation_key": "total_kwh",
            },
        },
    },
}

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
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
                "t4": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "outside_temperature",
                },
                "tank_actual_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "cur_temperature",
                }
            }
        }
    },
    "171000AU": _POOL_HEAT_PUMP_MAPPING,
    ("subtype", "513"): _POOL_HEAT_PUMP_MAPPING,
}
