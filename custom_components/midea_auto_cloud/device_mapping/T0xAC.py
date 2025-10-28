from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, PRECISION_WHOLE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
# from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}],
        "centralized": [],
        "entities": {
            Platform.FAN: {
                "fan": {
                    "power": "new_wind_machine",
                    "speeds": [
                        {"fresh_air_fan_speed": 20},
                        {"fresh_air_fan_speed": 40},
                        {"fresh_air_fan_speed": 60},
                        {"fresh_air_fan_speed": 80},
                        {"fresh_air_fan_speed": 100},
                    ],
                    "preset_modes": {
                        "heat_exchange": {
                            "fresh_air_mode": 1,
                            "wind_strength": 0
                        },
                        "smooth_in": {
                            "fresh_air_mode": 2,
                            "wind_strength": 0
                        },
                        "rough_in": {
                            "fresh_air_mode": 2,
                            "wind_strength": 1
                        },
                        "smooth_out": {
                            "fresh_air_mode": 3,
                            "wind_strength": 0
                        },
                        "rough_out": {
                            "fresh_air_mode": 3,
                            "wind_strength": 1
                        },
                        "auto": {
                            "fresh_air_mode": 4,
                            "wind_strength": 0
                        },
                        "innercycle": {
                            "fresh_air_mode": 5,
                            "wind_strength": 0
                        },
                    }
                }
            },
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "auto"},
                        "dry": {"power": "on", "mode": "dry"},
                        "fan_only": {"power": "on", "mode": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco": "off",
                            "comfort_power_save": "off",
                            "cool_power_saving": 0,
                            # "comfort_sleep": "off",
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "comfort": {"comfort_power_save": "on"},
                        # "sleep": {"comfort_sleep": "on"},
                        "boost": {"strong_wind": "on"}
                    },
                    "swing_modes": {
                        "off": {"wind_swing_lr": "off", "wind_swing_ud": "off"},
                        "both": {"wind_swing_lr": "on", "wind_swing_ud": "on"},
                        "horizontal": {"wind_swing_lr": "on", "wind_swing_ud": "off"},
                        "vertical": {"wind_swing_lr": "off", "wind_swing_ud": "on"},
                    },
                    "fan_modes": {
                        "silent": {"wind_speed": 20},
                        "low": {"wind_speed": 40},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 80},
                        "full": {"wind_speed": 100},
                        "auto": {"wind_speed": 102}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "indoor_temperature",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "fresh_air_remove_odor": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "dry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "prevent_straight_wind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "aux_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "indoor_humidity": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    },
    "106J6363": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "water_model_power",
                    "hvac_modes": {
                        "off": {"water_model_power": "off"},
                        "heat": {"water_model_power": "on", "water_model_temperature_auto": "off"},
                        "auto": {"water_model_power": "on", "water_model_temperature_auto": "on"},
                    },
                    "preset_modes": {
                        "none": {"water_model_go_out": "off"},
                        "go out": {"water_model_go_out": "on"},
                    },
                    "target_temperature": "water_model_temperature_set",
                    "min_temp": 25,
                    "max_temp": 60,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_WHOLE,
                }
            },
        }
    },
    "26093139": {
        "rationale": [0, 3],
        "queries": [{}, {"query_type": "run_status"}],
        "centralized": ["fresh_air", "fresh_air_mode", "fresh_air_fan_speed", "fresh_air_temp"],
        "entities": {
            Platform.FAN: {
                "fan": {
                    "power": "fresh_air",
                    "speeds": [
                        {"fresh_air": 3, "fresh_air_fan_speed": 20},
                        {"fresh_air": 3, "fresh_air_fan_speed": 40},
                        {"fresh_air": 3, "fresh_air_fan_speed": 60},
                        {"fresh_air": 3, "fresh_air_fan_speed": 80},
                        {"fresh_air": 3, "fresh_air_fan_speed": 100},
                    ],
                    "preset_modes": {
                        "heat_exchange": {
                            "fresh_air_mode": 1,
                            "wind_strength": 0
                        },
                        "smooth_in": {
                            "fresh_air_mode": 2,
                            "wind_strength": 0
                        },
                        "rough_in": {
                            "fresh_air_mode": 2,
                            "wind_strength": 1
                        },
                        "smooth_out": {
                            "fresh_air_mode": 3,
                            "wind_strength": 0
                        },
                        "rough_out": {
                            "fresh_air_mode": 3,
                            "wind_strength": 1
                        },
                        "auto": {
                            "fresh_air_mode": 4,
                            "wind_strength": 0
                        },
                        "innercycle": {
                            "fresh_air_mode": 5,
                            "wind_strength": 0
                        },
                    }
                }
            },
        }
    },
    "22012227": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": ["power", "temperature", "small_temperature", "mode", "eco", "comfort_power_save",
                        "strong_wind", "wind_swing_lr", "wind_swing_ud", "wind_speed",
                        "ptc", "dry"],
        
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "auto"},
                        "dry": {"power": "on", "mode": "dry"},
                        "fan_only": {"power": "on", "mode": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco": "off",
                            "comfort_power_save": "off",
                            # "comfort_sleep": "off",
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on"},
                        "comfort": {"comfort_power_save": "on"},
                        # "sleep": {"comfort_sleep": "on"},
                        "boost": {"strong_wind": "on"}
                    },
                    "swing_modes": {
                        "off": {"wind_swing_lr": "off", "wind_swing_ud": "off"},
                        "both": {"wind_swing_lr": "on", "wind_swing_ud": "on"},
                        "horizontal": {"wind_swing_lr": "on", "wind_swing_ud": "off"},
                        "vertical": {"wind_swing_lr": "off", "wind_swing_ud": "on"},
                    },
                    "fan_modes": {
                        "silent": {"wind_speed": 20},
                        "low": {"wind_speed": 40},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 80},
                        "full": {"wind_speed": 100},
                        "auto": {"wind_speed": 102}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "indoor_temperature",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "dry": {
                    "name": "干燥",
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "prevent_straight_wind": {
                    "name": "防直吹",
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [1, 2]
                },
                "aux_heat": {
                    "name": "电辅热",
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "outdoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    },
    # Colmo Turing Central AC indoor units, different cooling capacity models share the same config.
    ("22396961", "22396963", "22396965", "22396969", "22396973"): {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "translation_key": "colmo_turing_central_ac_climate",
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "fan_only": {"power": "on", "mode": "fan"},
                        "dry": {"power": "on", "mode": "dryauto"},
                        "auto": {"power": "on", "mode": "dryconstant"},
                        # Note:
                        # For Colmo Turing AC, dry and auto mode is not displayed in the app/controller explicitly.
                        # Instead it defined 2 custom modes: dryauto (自动抽湿) and dryconstant (温湿灵控/恒温恒湿).
                        # So I mapped the custom modes to the similar pre-defineds:
                        #   - auto -> dryconstant (温湿灵控/恒温恒湿): able to set target T and H, and auto adjust them to maintain a comfortable environment.
                        #   - dry -> dryauto (自动抽湿): dehumidification mode, under which temperature is not adjustable.
                        # Translations are also modified (for only colmo_turing_central_ac_climate) accordingly.
                    },
                    "preset_modes": {
                        "none": {
                            "energy_save": "off",
                        },
                        "sleep": {"energy_save": "on"}
                    },
                    "fan_modes": {
                        "silent": {"wind_speed": 20},
                        "low": {"wind_speed": 40},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 80},
                        "full": {"wind_speed": 100},
                        "auto": {"wind_speed": 102}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "indoor_temperature",
                    "target_humidity": "dehumidity",
                    "current_humidity": "indoor_humidity",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 16,
                    "max_temp": 30,
                    "min_humidity": 45,
                    "max_humidity": 65,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "indoor_humidity": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "wind_speed_real": {
                    "device_class": SensorDeviceClass.WIND_SPEED,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                }
            },
            Platform.SWITCH: {
                "power": {
                    "name": "电源",
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
        }
    }
}
