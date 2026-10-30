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
    "760001EC": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": ["additional", "wash_region", "door_auto_open"],
        "entities": {
            Platform.SWITCH: {
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "airswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "auto_release_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dry_step_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [1, 0],
                },
                "dryswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.LOCK: {
                "lock": {
                    "translation_key": "child_lock",
                },
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {},
                "door_auto_open": {},
                "air_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "water_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "diy_flag": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
            },
            Platform.SENSOR: {
                "mode": {},
                "work_status": {},
                "operator": {},
                "additional": {},
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
                "air_set_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "dry_set_min": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
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
                "wash_mode": {
                    "options": {
                        "neutral_gear": {"work_status": "cancel", "mode": "null"},
                        "auto_wash": {"work_status": "work", "mode": "auto"},
                        "strong_wash": {"work_status": "work", "mode": "intensive"},
                        "standard_wash": {"work_status": "work", "mode": "normal"},
                        "eco_wash": {"work_status": "work", "mode": "eco"},
                        "glass_wash": {"work_status": "work", "mode": "glass"},
                        "90min_wash": {"work_status": "work", "mode": "90min"},
                        "fast_wash": {"work_status": "work", "mode": "rapid"},
                        "soak_wash": {"work_status": "work", "mode": "soak"},
                        "hour_wash": {"work_status": "work", "mode": "1hour"},
                        "3in1": {"work_status": "work", "mode": "3in1"},
                        "auto_heavy": {"work_status": "work", "mode": "auto_heavy"},
                        "party": {"work_status": "work", "mode": "party"},
                        "quietnight_wash": {"work_status": "work", "mode": "quiet"},
                        "auto_daily": {"work_status": "work", "mode": "auto_daily"},
                        "germ": {"work_status": "work", "mode": "hygiene"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "auto_glass": {"work_status": "work", "mode": "auto_glass"},
                        "baby_care": {"work_status": "work", "mode": "baby_care"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit"},
                        "45min_wash": {"work_status": "work", "mode": "45min"},
                        "anion1": {"work_status": "work", "mode": "anion1"},
                        "anion2": {"work_status": "work", "mode": "anion2"},
                        "anion3": {"work_status": "work", "mode": "anion3"},
                        "low_degree": {"work_status": "work", "mode": "low_degree"},
                        "dry_only": {"work_status": "work", "mode": "dry_only"},
                        "dry_only_2h": {"work_status": "work", "mode": "dry_only_2h"},
                        "dry_only_3h": {"work_status": "work", "mode": "dry_only_3h"},
                        "dry_only_4h": {"work_status": "work", "mode": "dry_only_4h"},
                        "hot_air_1": {"work_status": "work", "mode": "hot_air_1"},
                        "hot_air_2": {"work_status": "work", "mode": "hot_air_2"},
                        "hot_air_3": {"work_status": "work", "mode": "hot_air_3"},
                    }
                },
                "wash_region": {
                    "options": {
                        "1": {"wash_region": 1},
                        "2": {"wash_region": 2},
                        "3": {"wash_region": 3},
                    }
                },
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


# COLMO CDG18QHS1A; validated only for this SN8.
DEVICE_MAPPING["76000029"] = {'manufacturer': 'COLMO',
 'rationale': [0, 1],
 'queries': [{}],
 'centralized': [],
 'calculate': {'get': [{'lvalue': '[power_state]',
                        'rvalue': "'power_off' if [work_status] == 'power_off' else 'power_on'"},
                       {'lvalue': '[display_status]',
                        'rvalue': "'paused' if [work_status] == 'work' and [operator] == 'pause' "
                                  'else [work_status]'},
                       {'lvalue': '[display_mode]', 'rvalue': '[mode]'},
                       {'lvalue': '[runtime_left_time]',
                        'rvalue': "[left_time] if [work_status] == 'work' else None"},
                       {'lvalue': '[reservation_remaining]',
                        'rvalue': '([order_left_hour] or 0) * 60 + ([order_left_min] or 0) if '
                                  "[work_status] == 'order' else None"}]},
 'entities': {'binary_sensor': {'doorswitch': {'device_class': 'door',
                                               'rationale': [1, 0],
                                               'translation_key': 'colmo_doorswitch'},
                                'softwater_lack': {'device_class': 'problem',
                                                   'translation_key': 'colmo_softwater_lack'},
                                'bright_lack': {'device_class': 'problem',
                                                'translation_key': 'colmo_bright_lack'},
                                'water_lack': {'device_class': 'problem',
                                               'translation_key': 'colmo_water_lack'}},
              'sensor': {'display_status': {'translation_key': 'colmo_display_status',
                                            'device_class': 'enum',
                                            'options': ['power_off',
                                                        'power_on',
                                                        'cancel',
                                                        'work',
                                                        'paused',
                                                        'order',
                                                        'error']},
                         'mode': {'translation_key': 'colmo_mode',
                                  'device_class': 'enum',
                                  'options': ['auto_wash',
                                              'strong_wash',
                                              'standard_wash',
                                              'hour_wash',
                                              'soak_wash',
                                              'eco_wash',
                                              'germ',
                                              'glass_wash',
                                              'fast_wash',
                                              'quietnight_wash',
                                              'neutral_gear',
                                              'cloud_wash']},
                         'temperature': {'device_class': 'temperature',
                                         'unit_of_measurement': '°C',
                                         'state_class': 'measurement',
                                         'translation_key': 'colmo_temperature'},
                         'left_time': {'device_class': 'duration',
                                       'unit_of_measurement': 'min',
                                       'attribute': 'runtime_left_time',
                                       'translation_key': 'colmo_left_time'},
                         'error_code': {'translation_key': 'colmo_error_code'},
                         'wash_stage': {'translation_key': 'colmo_wash_stage'},
                         'reservation_remaining': {'device_class': 'duration',
                                                   'unit_of_measurement': 'min',
                                                   'translation_key': 'colmo_reservation_remaining'}},
              'switch': {'power': {'attribute': 'work_status',
                                   'state_attribute': 'power_state',
                                   'rationale': ['power_off', 'power_on'],
                                   'translation_key': 'colmo_power'},
                         'child_lock': {'attribute': 'lock',
                                        'rationale': ['off', 'on'],
                                        'translation_key': 'colmo_child_lock'},
                         'beep': {'attribute': 'switch',
                                  'state_attribute': 'beep_control',
                                  'rationale': [0, 1],
                                  'command': {'common_down_type': 5},
                                  'translation_key': 'colmo_beep'}},
              'button': {'pause': {'command': {'operator': 'pause'},
                                   'translation_key': 'colmo_pause'},
                         'resume': {'command': {'operator': 'start'},
                                    'translation_key': 'colmo_resume'},
                         'cancel': {'command': {'work_status': 'cancel'},
                                    'translation_key': 'colmo_cancel'},
                         'start': {'requires_idle': True,
                                   'command': {'work_status': 'work'},
                                   'include_attributes': {'mode': 'selected_program',
                                                          'wash_region': 'selected_region',
                                                          'additional': 'selected_additional'},
                                   'translation_key': 'colmo_start'},
                         'reserve': {'requires_idle': True,
                                     'command': {'work_status': 'order'},
                                     'include_attributes': {'mode': 'selected_program',
                                                            'wash_region': 'selected_region',
                                                            'additional': 'selected_additional'},
                                     'delay_attribute': 'reservation_delay_minutes',
                                     'requires_power_on': True,
                                     'translation_key': 'colmo_reserve'},
                         'cancel_reservation': {'condition': {'eq': ['work_status', 'order']},
                                                'command': {'work_status': 'cancel_order'},
                                                'translation_key': 'colmo_cancel_reservation'}},
              'select': {'program_selection': {'attribute': 'selected_program',
                                               'status_key': 'selected_program',
                                               'requires_idle': True,
                                               'default_value': 'standard_wash',
                                               'options': {'auto_wash': {'selected_program': 'auto_wash'},
                                                           'strong_wash': {'selected_program': 'strong_wash'},
                                                           'standard_wash': {'selected_program': 'standard_wash'},
                                                           'hour_wash': {'selected_program': 'hour_wash'},
                                                           'soak_wash': {'selected_program': 'soak_wash'},
                                                           'eco_wash': {'selected_program': 'eco_wash'},
                                                           'germ': {'selected_program': 'germ'},
                                                           'glass_wash': {'selected_program': 'glass_wash'},
                                                           'fast_wash': {'selected_program': 'fast_wash'},
                                                           'quietnight_wash': {'selected_program': 'quietnight_wash'}},
                                               'reset_draft_parameters': {'selected_region': 3,
                                                                          'selected_additional': 0},
                                               'translation_key': 'colmo_program_selection'},
                         'region_selection': {'attribute': 'selected_region',
                                              'status_key': 'selected_region',
                                              'default_value': 3,
                                              'requires_idle': True,
                                              'condition': {'eq': ['selected_program',
                                                                   'standard_wash']},
                                              'options': {'upper': {'selected_region': 1},
                                                          'lower': {'selected_region': 2},
                                                          'all': {'selected_region': 3}},
                                              'translation_key': 'colmo_region_selection'},
                         'additional_selection': {'attribute': 'selected_additional',
                                                  'status_key': 'selected_additional',
                                                  'default_value': 0,
                                                  'requires_idle': True,
                                                  'condition': {'eq': ['selected_program',
                                                                       'standard_wash']},
                                                  'options': {'none': {'selected_additional': 0},
                                                              'once': {'selected_additional': 9},
                                                              'twice': {'selected_additional': 10}},
                                                  'translation_key': 'colmo_additional_selection'}},
              'number': {'reservation_delay_minutes': {'default_value': 120,
                                                       'min': 1,
                                                       'max': 1440,
                                                       'step': 1,
                                                       'unit_of_measurement': 'min',
                                                       'translation_key': 'colmo_reservation_delay_minutes'},
                         'softwater': {'min': 1,
                                       'max': 6,
                                       'step': 1,
                                       'translation_key': 'colmo_softwater'},
                         'bright': {'min': 1,
                                    'max': 5,
                                    'step': 1,
                                    'translation_key': 'colmo_bright'}}},
 'write_attributes': ['common_down_type', 'switch', 'order_set_hour', 'order_set_min'],
 'cloud_queries': {'water_power': False},
 'capabilities': {'prefer_cloud_lua': True,
                  'confirm_status_after_control': {'attempts': 4,
                                                   'interval': 0.5,
                                                   'work_status': {'power_on': ['power_on',
                                                                                'cancel'],
                                                                   'power_off': ['power_off'],
                                                                   'cancel': ['cancel'],
                                                                   'cancel_order': ['cancel'],
                                                                   'order': ['order'],
                                                                   'work': ['work']}}}}
