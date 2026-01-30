from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, PRECISION_WHOLE, \
    CONCENTRATION_PARTS_PER_MILLION, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
# from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}, {"query_type":"indoor_humidity"}, {"query_type":"indoor_temperature"}],
        "centralized": [],
        "entities": {
            Platform.FAN: {
                "fan": {
                    "power": "new_wind_machine",
                    "speeds": list({"fresh_air_fan_speed": value + 1} for value in range(0, 100)),
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
                },
            },
            Platform.SELECT: {
                "follow_body_sense": {
                    "options": {
                        "on": {"follow_body_sense": "on", "follow_body_sense_enable": 1},
                        "off": {"follow_body_sense": "off", "follow_body_sense_enable": 1},
                    }
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
            }
        }
    },
    "21293193": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "query_all"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "smart_mode"},
                    },
                    "preset_modes": {
                        "auto": {"water_model_temperature_auto": "on", "temperature_control_switch": 0},
                        "manual": {"water_model_temperature_auto": "off", "temperature_control_switch": 0},
                        "link": {"water_model_temperature_auto": "on", "temperature_control_switch": 1}
                    },
                    "target_temperature": "effluent_temperature",
                    "pre_mode": "mode",
                    "min_temp": 25,
                    "max_temp": 60,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.NUMBER: {
                "temperature": {
                    "min": 16,
                    "max": 30,
                    "step": 0.5,
                    "translation_key": "heating_target_temperature",
                },
            },
            Platform.SWITCH: {
                "out_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                    "translation_key": "water_model_go_out",
                },
                "mute_voice": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                    "translation_key": "mute",
                },
                "eco": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "temperature_control_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                    "translation_key": "room_temp_ctrl",
                },
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                }
            }
        }
    },
    "22259015": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "run_status"}, {"query_type": "module_30"}, {"query_type": "module_31"},
                    {"query_type": "module_32"}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[indoor_humidity]",
                    "rvalue": "[humidity_value]"
                },
                {
                    "lvalue": "[indoor_temperature]",
                    "rvalue": "[t1_temp]"
                },
                {
                    "lvalue": "[co2_value]",
                    "rvalue": "[co2_concentration]"
                },
                {
                    "lvalue": "[pm25_value]",
                    "rvalue": "[dust_co2]"
                }
            ],
            "set": []
        },
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
                            "cool_power_saving": 0,
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "comfort": {"comfort_power_save": "on"},
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
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "prevent_straight_wind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "aux_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "elec_dust_remove": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "auto_comfort_fresh_air": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "auto_fresh_off_co2": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "comfort_fresh_air": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "manul_humi":{
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "remove_arofene":{
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "disinfect":{
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "remove_peculiar_smell":{
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                    "condition": {
                        "not": ["remove_peculiar_smell", "air_exhaust"]
                    }
                },
                "air_exhaust": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                    "condition": {
                        "not": ["remove_peculiar_smell", "air_exhaust"]
                    }
                },
                "down_wind_left_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [1, 0],
                    "condition": {
                        "not": ["down_wind_left_switch", "down_wind_right_switch"]
                    }
                },
                "down_wind_right_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [1, 0],
                    "condition": {
                        "not": ["down_wind_left_switch", "down_wind_right_switch"]
                    }
                }
            },
            Platform.NUMBER: {
                "manul_humi_value": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "min": 40,
                    "max": 70,
                    "step": 1,
                    "unit_of_measurement": "%",
                    "mode": "slider"
                },
                "auto_purifier_on_pm": {
                    "device_class": SensorDeviceClass.PM25,
                    "min": 75,
                    "max": 180,
                    "step": 1,
                    "unit_of_measurement": "µg/m³",
                    "mode": "slider",
                    "icon": "mdi:air-filter"
                }
            },
            Platform.SELECT: {
                "fresh_air_fan_speed": {
                    "device_class": "enum",
                    "query": "fresh_air_fan_speed",
                    "value_mapping": {
                        40: "低速",
                        60: "中速",
                        80: "高速",
                        100: "全速"
                    },
                    "options": {
                        "低速": {"fresh_air_fan_speed": 40},
                        "中速": {"fresh_air_fan_speed": 60},
                        "高速": {"fresh_air_fan_speed": 80},
                        "全速": {"fresh_air_fan_speed": 100}
                    }
                },
                "fresh_air_setting_mode": {
                    "device_class": "enum",
                    "query": "fresh_air_setting_mode",
                    "value_mapping": {
                        0: "内外循环",
                        1: "外循环"
                    },
                    "options": {
                        "内外循环": {"fresh_air_setting_mode": 0},
                        "外循环": {"fresh_air_setting_mode": 1}
                    },
                    "condition": {
                        "eq": ["comfort_fresh_air", 1]
                    }
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
                "co2_value": {
                    "device_class": SensorDeviceClass.CO2,
                    "unit_of_measurement": CONCENTRATION_PARTS_PER_MILLION,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "pm25_value": {
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
            }
        }
    },
    ("22019031", "22019035", "22019045"): {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"fresh_air"}, {"query_type":"indoor_humidity"}, {"query_type":"indoor_temperature"}, {"query_type":"outdoor_temperature"}],
        "centralized": [],
        "entities": {
            Platform.FAN: {
                "fan": {
                    "power": "fresh_air",
                    "speeds": [
                        {"fresh_air": "on", "fresh_air_fan_speed": 40},
                        {"fresh_air": "on", "fresh_air_fan_speed": 60},
                        {"fresh_air": "on", "fresh_air_fan_speed": 80},
                        {"fresh_air": "on", "fresh_air_fan_speed": 100}
                    ],
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
                },
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
                "fresh_air_temp": {
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
    "17497071": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "water_model_run_status"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "water_model_power",
                    "hvac_modes": {
                        "off": {"water_model_power": "off"},
                        "heat": {"water_model_power": "on"},
                    },
                    "preset_modes": {
                        "auto": {"water_model_temperature_auto": "on", "water_temp_linkage_switch": 0},
                        "link": {"water_model_temperature_auto": "off", "water_temp_linkage_switch": 1},
                        "manual": {"water_model_temperature_auto": "off", "water_temp_linkage_switch": 0}
                    },
                    "target_temperature": "water_model_temperature_set",
                    "current_temperature": ["temperature", "small_temperature"],
                    "pre_mode": "mode",
                    "aux_heat": "water_model_ptc",
                    "min_temp": 25,
                    "max_temp": 60,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "water_model_power_save": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_model_go_out": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_model_ptc": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "aux_heat",
                },
            },
            Platform.SENSOR: {
                "tw1_in_water_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "tw1_out_water_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "humidity": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    },
    "10693145": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "water_model_run_status"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "water_model_power",
                    "hvac_modes": {
                        "off": {"water_model_power": "off"},
                        "heat": {"water_model_power": "on"},
                    },
                    "preset_modes": {
                        "auto": {"water_model_temperature_auto": "on", "water_temp_linkage_switch": 0},
                        "link": {"water_model_temperature_auto": "off", "water_temp_linkage_switch": 1},
                        "manual": {"water_model_temperature_auto": "off", "water_temp_linkage_switch": 0}
                    },
                    "target_temperature": "water_model_temperature_set",
                    "current_temperature": ["tw_out_water_temp", "small_temperature"],
                    "pre_mode": "mode",
                    "aux_heat": "water_model_ptc",
                    "min_temp": 25,
                    "max_temp": 60,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "water_model_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_model_power_save": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_model_go_out": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SENSOR: {
                "tw1_in_water_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "tw_out_water_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
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
                    "speeds": list({"fresh_air": 3, "fresh_air_fan_speed": value + 1} for value in range(0, 100)),
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
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "prevent_straight_wind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [1, 2]
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
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
        }
    },
    "23096653": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}, {"query_type":"indoor_humidity"}, {"query_type":"indoor_temperature"}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[total_elec_value]",
                    "rvalue": "float([total_elec]) / 1000"
                },
            ],
        },
        "centralized": [],
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
                            "cool_power_saving": 0,
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "boost": {"strong_wind": "on"}
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
                "fengguan_remove_odor": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["on", "off"],
                    "translation_key": "disinfect",
                },
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ptc": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "aux_heat",
                }
            },
            Platform.SELECT: {
                "follow_body_sense": {
                    "options": {
                        "on": {"follow_body_sense": "on", "follow_body_sense_enable": 1},
                        "off": {"follow_body_sense": "off", "follow_body_sense_enable": 1},
                    }
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
                "total_elec_value": {
                    "device_class": SensorDeviceClass.ENERGY,
                    "unit_of_measurement": "kWh",
                    "state_class": SensorStateClass.TOTAL_INCREASING
                }
            }
        }
    },
    "23096633": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}, {"query_type":"indoor_humidity"}, {"query_type":"indoor_temperature"}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[total_elec_value]",
                    "rvalue": "float([total_elec]) / 1000"
                },
            ],
        },
        "centralized": [],
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
                            "cool_power_saving": 0,
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "boost": {"strong_wind": "on"}
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
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ptc": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "aux_heat",
                }
            },
            Platform.SELECT: {
                "new_wind_model_intake_enable": {
                    "options": {
                        "off": {"new_wind_model_intake_switch": "off"},
                        "low": {"new_wind_model_intake_switch": "on", "new_wind_model_intake_wind": "40"},
                        "medium": {"new_wind_model_intake_switch": "on", "new_wind_model_intake_wind": "60"},
                        "high": {"new_wind_model_intake_switch": "on", "new_wind_model_intake_wind": "80"},
                        "full": {"new_wind_model_intake_switch": "on", "new_wind_model_intake_wind": "100"}
                    }
                },
                "new_wind_model_exhaust_enable": {
                    "options": {
                        "off": {"new_wind_model_exhaust_switch": "off"},
                        "silent": {"new_wind_model_exhaust_switch": "on", "new_wind_model_exhaust_wind": "20"},
                        "high": {"new_wind_model_exhaust_switch": "on", "new_wind_model_exhaust_wind": "80"},
                        "full": {"new_wind_model_exhaust_switch": "on", "new_wind_model_exhaust_wind": "100"}
                    }
                },
                "follow_body_sense": {
                    "options": {
                        "on": {"follow_body_sense": "on", "follow_body_sense_enable": 1},
                        "off": {"follow_body_sense": "off", "follow_body_sense_enable": 1},
                    }
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
                "total_elec_value": {
                    "device_class": SensorDeviceClass.ENERGY,
                    "unit_of_measurement": "kWh",
                    "state_class": SensorStateClass.TOTAL_INCREASING
                }
            }
        }
    },
    "26096947": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}],
        "centralized": [],
        "entities": {
            Platform.SELECT: {
                "fresh_air_mode_select": {
                    "translation_key": "fresh_air_mode_select",
                    "device_class": "enum",
                    "options": {
                        "normal": {"fresh_air_mode": 1},
                        "smart": {"fresh_air_mode": 4},
                        "manual_recirculation": {"fresh_air_mode": 5},
                        "auto_recirculation": {"fresh_air_mode": 6},
                        "supply_air_gentle": {"fresh_air_mode": 2, "wind_strength": 0},
                        "supply_air_fast": {"fresh_air_mode": 2, "wind_strength": 1},
                        "exhaust_air_gentle": {"fresh_air_mode": 3, "wind_strength": 0},
                        "exhaust_air_fast": {"fresh_air_mode": 3, "wind_strength": 1}
                    }
                }
            },
            Platform.SWITCH: {
                "new_wind_machine": {
                    "translation_key": "new_wind_machine",
                    "device_class": SwitchDeviceClass.SWITCH
                },
                "anion_status": {
                    "translation_key": "anion_status",
                    "device_class": SwitchDeviceClass.SWITCH,
				    "rationale": [0, 1]
                }
            },
            Platform.NUMBER: {
			    "fresh_air_fan_speed": {
                    "translation_key": "fresh_air_fan_speed",
				    "unit_of_measurement": "%",
				    "min": 1,
				    "max": 100,
				    "step": 1
			    }
            },
		    Platform.SENSOR: {
                "fresh_filter_time": {
                    "translation_key": "fresh_filter_time",
                    "device_class": "percentage",
                    "unit_of_measurement": "%"
                },
                "new_wind_humidity": {
                    "translation_key": "new_wind_humidity",
                    "device_class": "humidity",
                    "unit_of_measurement": "%"
                },
                "new_wind_outdoor_temperature": {
                    "translation_key": "new_wind_outdoor_temperature",
                    "device_class": "temperature",
                    "unit_of_measurement": "°C"
                }
            }
        }
    },
    ("22040023", "22270043"): {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "run_status"}, {"query_type": "indoor_temperature"}],
        "centralized": ["power", "temperature", "mode", "eco", "comfort_power_save",
                        "wind_swing_lr", "wind_swing_ud", "wind_speed", "ptc", "dry"],
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
                            "comfort_power_save": "off"
                        },
                        "eco": {"eco": "on"},
                        "comfort": {"comfort_power_save": "on"}
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
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ptc": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "aux_heat",
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
                }
            }
        }
    }
}
