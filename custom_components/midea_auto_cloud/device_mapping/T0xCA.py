from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "freezing_mode", "intelligent_mode", "energy_saving_mode", "holiday_mode",
            "moisturize_mode", "preservation_mode", "acme_freezing_mode", "variable_mode",
            "storage_power", "left_flexzone_power", "right_flexzone_power", "freezing_power",
            "function_zone_power", "storage_temperature", "freezing_temperature",
            "left_flexzone_temperature", "right_flexzone_temperature"
        ],
        "entities": {
            Platform.SWITCH: {
                "freezing_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "intelligent_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "energy_saving_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "holiday_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "moisturize_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "preservation_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "acme_freezing_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "storage_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "left_flexzone_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "right_flexzone_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "freezing_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "function_zone_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cross_peak_electricity": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "all_refrigeration_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "remove_dew_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "humidify_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "unfreeze_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "floodlight_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "radar_mode_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "milk_mode_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "icea_mode_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "plasma_aseptic_mode_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "acquire_icea_mode_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "brash_icea_mode_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "acquire_water_mode_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "freezing_ice_machine_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "microcrystal_fresh": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dry_zone": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "electronic_smell": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "eradicate_pesticide_residue": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "performance_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ice_mouth_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.BINARY_SENSOR: {
                "storage_door_state": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "freezer_door_state": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "flexzone_door_state": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "storage_ice_home_door_state": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "bar_door_state": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "is_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            },
            Platform.CLIMATE: {
                "storage_zone": {
                    "power": "storage_power",
                    "hvac_modes": {
                        "off": {"storage_power": "off"},
                        "heat": {"storage_power": "on"}
                    },
                    "target_temperature": "storage_temperature",
                    "current_temperature": "refrigeration_real_temperature",
                    "min_temp": -10,
                    "max_temp": 10,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "freezing_zone": {
                    "power": "freezing_power",
                    "hvac_modes": {
                        "off": {"freezing_power": "off"},
                        "heat": {"freezing_power": "on"}
                    },
                    "target_temperature": "freezing_temperature",
                    "current_temperature": "freezing_real_temperature",
                    "min_temp": -30,
                    "max_temp": -10,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "left_flexzone": {
                    "power": "left_flexzone_power",
                    "hvac_modes": {
                        "off": {"left_flexzone_power": "off"},
                        "heat": {"left_flexzone_power": "on"}
                    },
                    "target_temperature": "left_flexzone_temperature",
                    "current_temperature": "left_variable_real_temperature",
                    "min_temp": -30,
                    "max_temp": 10,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "right_flexzone": {
                    "power": "right_flexzone_power",
                    "hvac_modes": {
                        "off": {"right_flexzone_power": "off"},
                        "heat": {"right_flexzone_power": "on"}
                    },
                    "target_temperature": "right_flexzone_temperature",
                    "current_temperature": "right_variable_real_temperature",
                    "min_temp": -30,
                    "max_temp": 10,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SELECT: {
                "variable_mode": {
                    "options": {
                        "none_mode": {"variable_mode": "none_mode"},
                        "freezing": {"variable_mode": "freezing"},
                        "refrigeration": {"variable_mode": "refrigeration"},
                        "wine": {"variable_mode": "wine"},
                        "vegetable": {"variable_mode": "vegetable"}
                    }
                },
                "icea_bar_function_switch": {
                    "options": {
                        "default": {"icea_bar_function_switch": "default"},
                        "ice": {"icea_bar_function_switch": "ice"},
                        "water": {"icea_bar_function_switch": "water"},
                        "off": {"icea_bar_function_switch": "off"}
                    }
                },
                "food_site": {
                    "options": {
                        "left_freezing_room": {"food_site": "left_freezing_room"},
                        "right_freezing_room": {"food_site": "right_freezing_room"},
                        "storage_room": {"food_site": "storage_room"},
                        "function_zone": {"food_site": "function_zone"}
                    }
                },
                "temperature_unit": {
                    "options": {
                        "celsius": {"temperature_unit": "celsius"},
                        "fahrenheit": {"temperature_unit": "fahrenheit"}
                    }
                }
            },
            Platform.SENSOR: {
                "storage_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "freezing_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_flexzone_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "right_flexzone_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "refrigeration_real_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "freezing_real_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_variable_real_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "right_variable_real_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "interval_room_humidity_level": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "normal_zone_level": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "function_zone_level": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "freeze_fahrenheit_level": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "refrigeration_fahrenheit_level": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "leach_expire_day": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "power_consumption_low": {
                    "device_class": SensorDeviceClass.POWER,
                    "unit_of_measurement": "W",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "power_consumption_high": {
                    "device_class": SensorDeviceClass.POWER,
                    "unit_of_measurement": "W",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "fast_cold_minute": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "fast_freeze_minute": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "version": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
