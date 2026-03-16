from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "0x11"}, {"query_type": "0x12"}],
        "centralized": [
            "power_state", "run_mode", "temp_set", "heat_enable", "cool_enable"
        ],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power_state",
                    "hvac_modes": {
                        "off": {"power_state": "off"},
                        "heat": {"power_state": "on", "run_mode": "heat", "heat_enable": "on"},
                        "cool": {"power_state": "on", "run_mode": "cool", "cool_enable": "on"},
                        "auto": {"power_state": "on", "run_mode": "auto", "heat_enable": "on", "cool_enable": "on"}
                    },
                    "target_temperature": "temp_set",
                    "current_temperature": "cur_temp",
                    "pre_mode": "mode",
                    "min_temp": 5,
                    "max_temp": 70,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "thermostat_1": {
                    "power": "thermostat_power_state1",
                    "hvac_modes": {
                        "off": {"thermostat_power_state1": "off"},
                        "auto": {"thermostat_power_state1": "on"},
                    },
                    "preset_modes": {
                        "none": {"thermostat_power_state1": "off"},
                        "heat": {
                            "thermostat_power_state1": "on",
                            "mode_set1": "2",
                        },
                        "cool": {
                            "thermostat_power_state1": "on",
                            "mode_set1": "1",
                        },
                        "fan_only": {
                            "thermostat_power_state1": "on",
                            "mode_set1": "0",
                        },
                        "ground": {
                            "thermostat_power_state1": "on",
                            "mode_set1": "3",
                        },
                        "heat_ground": {
                            "thermostat_power_state1": "on",
                            "mode_set1": "4",
                        },
                    },
                    "fan_modes": {
                        "auto": {"fan_level_set1": "0"},
                        "low": {"fan_level_set1": "1"},
                        "medium": {"fan_level_set1": "2"},
                        "high": {"fan_level_set1": "3"}
                    },
                    "target_temperature": "temp_set1",
                    "current_temperature": "room_temp1",
                    "pre_mode": "mode_set1",
                    "min_temp": 5,
                    "max_temp": 70,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "thermostat_2": {
                    "power": "thermostat_power_state2",
                    "hvac_modes": {
                        "off": {"thermostat_power_state2": "off"},
                        "auto": {"thermostat_power_state2": "on"},
                    },
                    "preset_modes": {
                        "none": {"thermostat_power_state2": "off"},
                        "heat": {
                            "thermostat_power_state2": "on",
                            "mode_set2": "2",
                        },
                        "cool": {
                            "thermostat_power_state2": "on",
                            "mode_set2": "1",
                        },
                        "fan_only": {
                            "thermostat_power_state2": "on",
                            "mode_set2": "0",
                        },
                        "ground": {
                            "thermostat_power_state2": "on",
                            "mode_set2": "3",
                        },
                        "heat_ground": {
                            "thermostat_power_state2": "on",
                            "mode_set2": "4",
                        },
                    },
                    "fan_modes": {
                        "auto": {"fan_level_set2": "0"},
                        "low": {"fan_level_set2": "1"},
                        "medium": {"fan_level_set2": "2"},
                        "high": {"fan_level_set2": "3"}
                    },
                    "target_temperature": "temp_set2",
                    "current_temperature": "room_temp2",
                    "pre_mode": "mode_set2",
                    "min_temp": 5,
                    "max_temp": 70,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "thermostat_3": {
                    "power": "thermostat_power_state3",
                    "hvac_modes": {
                        "off": {"thermostat_power_state3": "off"},
                        "auto": {"thermostat_power_state3": "on"},
                    },
                    "preset_modes": {
                        "none": {"thermostat_power_state3": "off"},
                        "heat": {
                            "thermostat_power_state3": "on",
                            "mode_set3": "2",
                        },
                        "cool": {
                            "thermostat_power_state3": "on",
                            "mode_set3": "1",
                        },
                        "fan_only": {
                            "thermostat_power_state3": "on",
                            "mode_set3": "0",
                        },
                        "ground": {
                            "thermostat_power_state3": "on",
                            "mode_set3": "3",
                        },
                        "heat_ground": {
                            "thermostat_power_state3": "on",
                            "mode_set3": "4",
                        },
                    },
                    "fan_modes": {
                        "auto": {"fan_level_set3": "0"},
                        "low": {"fan_level_set3": "1"},
                        "medium": {"fan_level_set3": "2"},
                        "high": {"fan_level_set3": "3"}
                    },
                    "target_temperature": "temp_set3",
                    "current_temperature": "room_temp3",
                    "pre_mode": "mode_set3",
                    "min_temp": 5,
                    "max_temp": 70,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "thermostat_4": {
                    "power": "thermostat_power_state4",
                    "hvac_modes": {
                        "off": {"thermostat_power_state4": "off"},
                        "auto": {"thermostat_power_state4": "on"},
                    },
                    "preset_modes": {
                        "none": {"thermostat_power_state4": "off"},
                        "heat": {
                            "thermostat_power_state4": "on",
                            "mode_set4": "2",
                        },
                        "cool": {
                            "thermostat_power_state4": "on",
                            "mode_set4": "1",
                        },
                        "fan_only": {
                            "thermostat_power_state4": "on",
                            "mode_set4": "0",
                        },
                        "ground": {
                            "thermostat_power_state4": "on",
                            "mode_set4": "3",
                        },
                        "heat_ground": {
                            "thermostat_power_state4": "on",
                            "mode_set4": "4",
                        },
                    },
                    "fan_modes": {
                        "auto": {"fan_level_set4": "0"},
                        "low": {"fan_level_set4": "1"},
                        "medium": {"fan_level_set4": "2"},
                        "high": {"fan_level_set4": "3"}
                    },
                    "target_temperature": "temp_set4",
                    "current_temperature": "room_temp4",
                    "pre_mode": "mode_set4",
                    "min_temp": 5,
                    "max_temp": 70,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
                "thermostat_5": {
                    "power": "thermostat_power_state5",
                    "hvac_modes": {
                        "off": {"thermostat_power_state5": "off"},
                        "auto": {"thermostat_power_state5": "on"},
                    },
                    "preset_modes": {
                        "none": {"thermostat_power_state5": "off"},
                        "heat": {
                            "thermostat_power_state5": "on",
                            "mode_set5": "2",
                        },
                        "cool": {
                            "thermostat_power_state5": "on",
                            "mode_set5": "1",
                        },
                        "fan_only": {
                            "thermostat_power_state5": "on",
                            "mode_set5": "0",
                        },
                        "ground": {
                            "thermostat_power_state5": "on",
                            "mode_set5": "3",
                        },
                        "heat_ground": {
                            "thermostat_power_state5": "on",
                            "mode_set5": "4",
                        },
                    },
                    "fan_modes": {
                        "auto": {"fan_level_set5": "0"},
                        "low": {"fan_level_set5": "1"},
                        "medium": {"fan_level_set5": "2"},
                        "high": {"fan_level_set5": "3"}
                    },
                    "target_temperature": "temp_set5",
                    "current_temperature": "room_temp5",
                    "pre_mode": "mode_set5",
                    "min_temp": 5,
                    "max_temp": 70,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                },
            },
            Platform.SWITCH: {
                "freeze_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "power_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "heat_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cool_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "silence_set_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "time_set_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "silence_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "holiday_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "holiday_set_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "holiday_on_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "room_temp_ctrl": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "room_temp_set": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "comp_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "day_time_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "week_time_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "warn_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "defrost_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "pre_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "energysaving_state1": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sleep_state1": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "energysaving_state2": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sleep_state2": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "energysaving_state3": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sleep_state3": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "energysaving_state4": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sleep_state4": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "energysaving_state5": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sleep_state5": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SELECT: {
                "run_mode": {
                    "options": {
                        "heat": {"run_mode": "heat"},
                        "cool": {"run_mode": "cool"},
                        "auto": {"run_mode": "auto"},
                        "fan": {"run_mode": "fan"},
                        "dry": {"run_mode": "dry"}
                    }
                },
                "temp_type": {
                    "options": {
                        "water_temperature": {"temp_type": "water_temperature"},
                        "room_temperature": {"temp_type": "room_temperature"},
                        "outdoor_temperature": {"temp_type": "outdoor_temperature"}
                    }
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "cur_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "heat_max_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "heat_min_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cool_max_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cool_min_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "auto_max_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "auto_min_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "preheat_on_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "preheat_max_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "preheat_min_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temp_set": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
