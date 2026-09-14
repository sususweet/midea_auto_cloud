from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "air_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "water_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "wash_stage": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "diy_flag": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_main_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_piao_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_times": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
            },
            Platform.SELECT: {
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
                "dryswitch": {
                    "options": {
                        "cancel": {"dryswitch": 0},
                        "waiting": {"dryswitch": 1},
                        "running": {"dryswitch": 2},
                    }
                },
                "dry_step_switch": {
                    "options": {
                        "cancel": {"dry_step_switch": 0},
                        "waiting": {"dry_step_switch": 1},
                        "running": {"dry_step_switch": 2},
                    }
                },
                "air_set_hour": {
                    "options": {
                        "12": {"air_set_hour": "12"},
                        "24": {"air_set_hour": "24"},
                        "36": {"air_set_hour": "36"},
                        "48": {"air_set_hour": "48"},
                        "60": {"air_set_hour": "60"},
                        "72": {"air_set_hour": "72"},
                    }
                },
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off"},
                        "power_on": {"work_status": "power_on"},
                        "cancel": {"work_status": "cancel"},
                        "pause": {"operator": "pause"},
                        "resume": {"operator": "start"},
                    }
                },
                "wash_mode": {
                    # Lua codecs (e.g. T_0000_E1_000W5601_*, T_0000_E1_76006481_*) expect
                    # mode strings like standard_wash / eco_wash. Unknown values fall back
                    # to eco (0x04) when work_status is work — which is the #244 symptom.
                    "options": {
                        "auto_wash": {"work_status": "work", "mode": "auto_wash"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "eco_wash": {"work_status": "work", "mode": "eco_wash"},
                        "glass_wash": {"work_status": "work", "mode": "glass_wash"},
                        "90min_wash": {"work_status": "work", "mode": "90min_wash"},
                        "fast_wash": {"work_status": "work", "mode": "fast_wash"},
                        "soak_wash": {"work_status": "work", "mode": "soak_wash"},
                        "hour_wash": {"work_status": "work", "mode": "hour_wash"},
                        "quietnight_wash": {"work_status": "work", "mode": "quietnight_wash"},
                        "germ": {"work_status": "work", "mode": "germ"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit_wash"},
                    }
                }
            },
            Platform.SENSOR: {
                "bright": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "softwater": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    },
    # WQP8-W7634C-W (and similar): Lua accepts short codec names (auto/normal/eco…).
    # Hardware-verified in #229; must NOT use *_wash payloads or programs fall back to ECO.
    # Comfee CDWI455i (built-in 45 cm dishwasher, EU market).
    #
    # Its Lua codec (T_0000_E1_10013080) only understands the short mode names,
    # e.g. luaTable["mode"] == "90min" -> 0x06. The "default" mapping sends
    # "90min_wash", which the codec does not recognise, so it falls back to
    # mode = 0x00 and the programme never starts. The appliance also reports the
    # short names back, e.g. mode = "90min".
    #
    # The programme list matches the ten programmes documented in the CDWI455i
    # user manual. Three of them ("glass_wash", "self_clean", "hour_wash") have
    # no button on the control panel and are cloud-only, so this integration is
    # the only way to start them besides the vendor app.
    #
    # "additional", "wash_region" and "door_auto_open" are encoded in the very
    # same packet as "mode" (bodyBytes[3], [4] and [13]), hence "centralized":
    # without it, starting a programme resets the wash zone and the automatic
    # door opening, which is enabled by default on this model.

    #
    # "mode" and "work_status" are also exposed as sensors: the selects only
    # resolve to an option while work_status == "work", and automations need the
    # raw value at any time (e.g. to tell "off" from "finished").
    #
    # Features the E1 protocol has but this model does not: uvswitch, waterswitch,
    # airswitch/air_set_hour/air_left_hour (dish storage with airing),
    # dryswitch/dry_step_switch and the diy_* group. They report constant or
    # meaningless values here, so they are left out.
    "7600016L": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": ["additional", "wash_region", "door_auto_open"],
        "entities": {
            Platform.LOCK: {
                "lock": {
                    "translation_key": "child_lock",
                },
            },
            Platform.BINARY_SENSOR: {
                # doorswitch == 1 means the door is CLOSED on this model, so no
                # BinarySensorDeviceClass.DOOR here - it would render "open".
                "doorswitch": {},
                "door_auto_open": {},
                "water_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
            },
            Platform.SENSOR: {
                "mode": {},
                "work_status": {},
                "operator": {},
                "additional": {},
                "wash_region": {},
                "wash_stage": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "cur_temperature"
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "remain_time"
                },
            },
            Platform.SELECT: {
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off"},
                        "power_on": {"work_status": "power_on"},
                        "cancel": {"work_status": "cancel"},
                        "pause": {"operator": "pause"},
                        "resume": {"operator": "start"},
                    }
                },
                # Programmes of the CDWI455i manual. Figures below are for
                # a full load: duration, energy, water.
                #   eco         50 C   198 min  0.674 kWh   9.4 L
                #   auto       55-65C  150 min  0.850-1.375 9.3-15.3 L
                #   intensive   72 C   178 min  1.326-1.356 13.9 L
                #   90min       55 C    90 min  0.830-0.930 10.4 L
                #   rapid       45 C    30 min  0.560 kWh   9.6 L
                #   hygiene     75 C   159 min  1.323-1.353 13.3 L
                #   quiet       55 C   240 min  0.890-0.970 9.9 L
                #   glass       47 C   120 min  0.760-0.805 12.7 L, cloud only
                #   self_clean  72 C   150 min  1.209-1.419 10.2 L, cloud only
                #   1hour       60 C    58 min  0.840 kWh   9.6 L,  cloud only
                #
                # Half load is "additional" == 2. It shortens the cycle as well
                # (hygiene 159 -> 125 min, 90min 90 -> 72), so the remaining
                # time reported before the start is the only reliable source of
                # the real cycle duration.
                "wash_mode": {
                    "options": {
                        "eco_wash": {"work_status": "work", "mode": "eco"},
                        "auto_wash": {"work_status": "work", "mode": "auto"},
                        "strong_wash": {"work_status": "work", "mode": "intensive"},
                        "90min_wash": {"work_status": "work", "mode": "90min"},
                        "fast_wash": {"work_status": "work", "mode": "rapid"},
                        "germ": {"work_status": "work", "mode": "hygiene"},
                        "quietnight_wash": {"work_status": "work", "mode": "quiet"},
                        "glass_wash": {"work_status": "work", "mode": "glass"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "hour_wash": {"work_status": "work", "mode": "1hour"},
                    }
                },
                # Water hardness H1..H6, factory setting H3.
                "softwater": {
                    "options": {
                        "1": {"softwater": 1},
                        "2": {"softwater": 2},
                        "3": {"softwater": 3},
                        "4": {"softwater": 4},
                        "5": {"softwater": 5},
                        "6": {"softwater": 6},
                    }
                },
                # Rinse aid dosage d1..d5, factory setting d3.
                "rinse_aid": {
                    "attribute": "bright",
                    "options": {
                        "1": {"bright": 1},
                        "2": {"bright": 2},
                        "3": {"bright": 3},
                        "4": {"bright": 4},
                        "5": {"bright": 5},
                    }
                },
            }
        }
    },
    "7600020L": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "air_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "water_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "wash_stage": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "diy_flag": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_main_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_piao_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_times": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
            },
            Platform.SELECT: {
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
                "dryswitch": {
                    "options": {
                        "cancel": {"dryswitch": 0},
                        "waiting": {"dryswitch": 1},
                        "running": {"dryswitch": 2},
                    }
                },
                "dry_step_switch": {
                    "options": {
                        "cancel": {"dry_step_switch": 0},
                        "waiting": {"dry_step_switch": 1},
                        "running": {"dry_step_switch": 2},
                    }
                },
                "air_set_hour": {
                    "options": {
                        "12": {"air_set_hour": "12"},
                        "24": {"air_set_hour": "24"},
                        "36": {"air_set_hour": "36"},
                        "48": {"air_set_hour": "48"},
                        "60": {"air_set_hour": "60"},
                        "72": {"air_set_hour": "72"},
                    }
                },
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off"},
                        "power_on": {"work_status": "power_on"},
                        "cancel": {"work_status": "cancel"},
                        "pause": {"operator": "pause"},
                        "resume": {"operator": "start"},
                    }
                },
                "wash_mode": {
                    "options": {
                        "auto_wash": {"work_status": "work", "mode": "auto"},
                        "strong_wash": {"work_status": "work", "mode": "intensive"},
                        "standard_wash": {"work_status": "work", "mode": "normal"},
                        "eco_wash": {"work_status": "work", "mode": "eco"},
                        "glass_wash": {"work_status": "work", "mode": "glass"},
                        "90min_wash": {"work_status": "work", "mode": "90min"},
                        "fast_wash": {"work_status": "work", "mode": "rapid"},
                        "soak_wash": {"work_status": "work", "mode": "soak"},
                        "hour_wash": {"work_status": "work", "mode": "1hour"},
                        "quietnight_wash": {"work_status": "work", "mode": "quiet"},
                        "germ": {"work_status": "work", "mode": "hygiene"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit"},
                    }
                }
            },
            Platform.SENSOR: {
                "bright": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "softwater": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    },
    "76006481": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "air_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "water_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "wash_stage": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "diy_flag": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_main_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_piao_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_times": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
            },
            Platform.NUMBER: {
                "air_set_hour": {
                    "min": 1,
                    "max": 72,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS
                }
            },
            Platform.SELECT: {
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
                "dryswitch": {
                    "options": {
                        "cancel": {"dryswitch": 0},
                        "waiting": {"dryswitch": 1},
                        "running": {"dryswitch": 2},
                    }
                },
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off"},
                        "power_on": {"work_status": "power_on"},
                        "cancel": {"work_status": "cancel"},
                        "pause": {"operator": "pause"},
                        "resume": {"operator": "start"},
                    }
                },
                "wash_mode": {
                    "options": {
                        "auto_wash": {"work_status": "work", "mode": "auto_wash"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "eco_wash": {"work_status": "work", "mode": "eco_wash"},
                        "glass_wash": {"work_status": "work", "mode": "glass_wash"},
                        "90min_wash": {"work_status": "work", "mode": "90min_wash"},
                        "fast_wash": {"work_status": "work", "mode": "fast_wash"},
                        "soak_wash": {"work_status": "work", "mode": "soak_wash"},
                        "hour_wash": {"work_status": "work", "mode": "hour_wash"},
                        "quietnight_wash": {"work_status": "work", "mode": "quietnight_wash"},
                        "germ": {"work_status": "work", "mode": "germ"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit_wash"},
                    }
                }
            },
            Platform.SENSOR: {
                "bright": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "softwater": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    },
    "7600649Q": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "air_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "water_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "wash_stage":{
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "diy_flag": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_main_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_piao_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_times": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
            },
            Platform.SELECT: {
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
                "dryswitch": {
                    "options": {
                        "cancel": {"dryswitch": 0},
                        "waiting": {"dryswitch": 1},
                        "running": {"dryswitch": 2},
                    }
                },
                "dry_step_switch": {
                    "options": {
                        "cancel": {"dry_step_switch": 0},
                        "waiting": {"dry_step_switch": 1},
                        "running": {"dry_step_switch": 2},
                    }
                },
                "air_set_hour": {
                     "options": {
                        "12": {"air_set_hour": "12" },
                        "24": {"air_set_hour": "24" },
                        "36": {"air_set_hour": "36" },
                        "48": {"air_set_hour": "48" },
                        "60": {"air_set_hour": "60" },
                        "72": {"air_set_hour": "72" },
                    }
                },
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off" },
                        "power_on": {"work_status": "power_on" },
                        "cancel": {"work_status": "cancel" },
                        "pause": {"operator":"pause"},
                        "resume": {"operator":"start"},
                    }
                },
                "wash_mode": {
                    "options": {
                        "auto_wash": {"work_status": "work", "mode": "auto_wash"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "eco_wash": {"work_status": "work", "mode": "eco_wash"},
                        "glass_wash": {"work_status": "work", "mode": "glass_wash"},
                        "90min_wash": {"work_status": "work", "mode": "90min_wash"},
                        "fast_wash": {"work_status": "work", "mode": "fast_wash"},
                        "soak_wash": {"work_status": "work", "mode": "soak_wash"},
                        "hour_wash": {"work_status": "work", "mode": "hour_wash"},
                        "quietnight_wash": {"work_status": "work", "mode": "quietnight_wash"},
                        "germ": {"work_status": "work", "mode": "germ"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit_wash"},
                    }
                }
            },
            Platform.SENSOR: {
                "bright": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "softwater": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    },
    "7600V1E7": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.LOCK: {
                "lock": {
                    "translation_key": "child_lock",
                },
            },
            Platform.NUMBER: {
                "air_set_hour": {
                    "min": 1,
                    "max": 72,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS
                }
            },
            Platform.SELECT: {
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off" },
                        "power_on": {"work_status": "power_on" },
                        "cancel": {"work_status": "cancel" },
                        "pause": {"operator":"pause"},
                        "resume": {"operator":"start"},
                    }
                },
                "wash_mode": {
                    "options": {
                        "auto_wash": {"work_status": "work", "mode": "auto_wash"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "eco_wash": {"work_status": "work", "mode": "eco_wash"},
                        "soft_wash": {"work_status": "work", "mode": "glass_wash"},
                        "fast_wash": {"work_status": "work", "mode": "fast_wash"},
                        "soak_wash": {"work_status": "work", "mode": "soak_wash"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit_wash"}
                    }
                }
            },
            Platform.SENSOR: {
                "bright": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    },
    "760Y0026": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": ["additional"],
        "entities": {
            Platform.LOCK: {
                "lock": {
                    "translation_key": "child_lock",
                },
            },
            Platform.SWITCH: {
                "airswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM
                },
                "air_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                }
            },
            Platform.NUMBER: {
                "air_set_hour": {
                    "min": 0,
                    "max": 72,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS
                }
            },
            Platform.SELECT: {
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off"},
                        "power_on": {"work_status": "power_on"},
                        "cancel": {"work_status": "cancel"},
                        "pause": {"operator": "pause"},
                        "resume": {"operator": "start"}
                    }
                },
                "wash_mode": {
                    "options": {
                        "neutral_gear": {"work_status": "cancel", "mode": "neutral_gear"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "single_disinfect": {"work_status": "work", "mode": "single_disinfect"},
                        "eco_wash": {"work_status": "work", "mode": "eco_wash"},
                        "glass_wash": {"work_status": "work", "mode": "glass_wash"},
                        "fast_wash": {"work_status": "work", "mode": "fast_wash"},
                        "soak_wash": {"work_status": "work", "mode": "soak_wash"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit_wash"},
                        "germ": {"work_status": "work", "mode": "germ"},
                        "seafood_wash": {"work_status": "work", "mode": "seafood_wash"},
                        "hotpot_wash": {"work_status": "work", "mode": "hotpot_wash"}
                    }
                },
                "softwater": {
                    "options": {
                        "1": {"softwater": 1},
                        "2": {"softwater": 2},
                        "3": {"softwater": 3},
                        "4": {"softwater": 4},
                        "5": {"softwater": 5},
                        "6": {"softwater": 6}
                    }
                },
                "rinse_aid": {
                    "options": {
                        "1": {"bright": 1},
                        "2": {"bright": 2},
                        "3": {"bright": 3},
                        "4": {"bright": 4},
                        "5": {"bright": 5}
                    }
                },
                "additional": {
                    "options": {
                        "none": {"additional": 0},
                        "extra_rinse_1": {"additional": 9},
                        "extra_rinse_2": {"additional": 10},
                        "few_dishes_extra_rinse_1": {"additional": 13},
                        "few_dishes_extra_rinse_2": {"additional": 14}
                    }
                }
            },
            Platform.SENSOR: {
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "cur_temperature"
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "remain_time"
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "wash_stage": {
                    "device_class": SensorDeviceClass.ENUM
                }
            }
        }
    }
}
