from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform, UnitOfTime, UnitOfArea
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "disturb"}, {"query_type": "parts"}],
        "centralized": [],
        "entities": {
            Platform.BUTTON: {
                "find": {
                    "command": {"query_type": "find"},
                }
            },
            Platform.VACUUM: {
                "vacuum": {
                    "control": "work_status",
                    "fan_speeds": {
                        "command": {"work_status": "switch"},
                        "options": {
                            "soft": {"fan_level": "soft"},
                            "normal": {"fan_level": "normal"},
                            "high": {"fan_level": "high"},
                            "super": {"fan_level": "super"}
                        }
                    },
                    "control_actions": {
                        "start": "work",
                        "stop": "stop",
                        "pause": "pause",
                        "return": "charge"
                    }
                }
            },
            Platform.NUMBER: {
                "voice_level": {
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "command": {
                        "work_status": "voice",
                        "voice_level": "{value}"
                    }
                },
            },
            Platform.SWITCH: {
                "carpet_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                    "command": {"work_status": "switch"}
                },
            },
            Platform.SELECT: {
                "set_status": {
                    "command": {"work_status": "disturb"},
                    "options": {
                        "on": {
                            "disturb_switch": "on",
                            "disturb_start_time": "00:00",
                            "disturb_end_time": "00:00"
                        },
                        "off": {
                            "disturb_switch": "off",
                        },
                    },
                    "translation_key": "disturb"
                },
                "speed": {
                    "command": {"work_status": "switch"},
                    "options": {
                        "low": {"speed": "low"},  # High-efficiency
                        "high": {"speed": "high"},  # Exhaustive
                    }
                },
                "fan_setting": {
                    "command": {"work_status": "switch"},
                    "include_current": ["fan_level", "water_level"],
                    "options": {
                        "off": {"fan_level": "off"},
                        "soft": {"fan_level": "soft"},
                        "low": {"fan_level": "low"},
                        "normal": {"fan_level": "normal"},
                        "high": {"fan_level": "high"},
                        "super": {"fan_level": "super"}
                    }
                },
                "water_level": {
                    "command": {"work_status": "switch"},
                    "include_current": ["fan_level", "water_level"],
                    "options": {
                        "dry": {"water_level": "off"},
                        "low": {"water_level": "low"},
                        "normal": {"water_level": "normal"},
                        "high": {"water_level": "high"}
                    }
                },
                "sweep_mop_mode": {
                    "options": {
                        "sweep_and_mop": {"sweep_mop_mode": "sweep_and_mop"},
                        "sweep": {"sweep_mop_mode": "sweep"},
                        "mop": {"sweep_mop_mode": "mop"},
                        "sweep_then_mop": {"sweep_mop_mode": "sweep_then_mop"}
                    }
                },
                "work_mode": {
                    "command": {"work_status": "work"},
                    "options": {
                        "sweep_and_mop": {"work_mode": "sweep_and_mop"},
                        "sweep": {"work_mode": "sweep"},
                        "mop": {"work_mode": "mop"},
                        "sweep_then_mop": {"work_mode": "sweep_then_mop"},
                        "error": {"work_mode": "error"},
                        "random": {"work_mode": "random"},
                        "arc": {"work_mode": "arc"},
                        "edge": {"work_mode": "edge"},
                        "emphases": {"work_mode": "emphases"},
                        "screw": {"work_mode": "screw"},
                        "bed": {"work_mode": "bed"},
                        "wide_screw": {"work_mode": "wide_screw"},
                        "auto": {"work_mode": "auto"},
                        "area": {"work_mode": "area"},
                        "zone_index": {"work_mode": "zone_index"},
                        "zone_rect": {"work_mode": "zone_rect"},
                        "path": {"work_mode": "path"},
                    }
                },
                "work_status": {
                    "options": {
                        "charge": {"work_status": "charge"},
                        "charge_pause": {"work_status": "charge_pause"},
                        "charge_continue": {"work_status": "charge_continue"},
                        "auto_clean": {"work_status": "auto_clean"},
                        "auto_clean_pause": {"work_status": "auto_clean_pause"},
                        "auto_clean_continue": {"work_status": "auto_clean_continue"},
                        "pause": {"work_status": "pause"},
                        "stop": {"work_status": "stop"},
                        "work": {"work_status": "work"},
                        "video_cruise_start": {"work_status": "video_cruise_start"},
                        "video_cruise_pause": {"work_status": "video_cruise_pause"},
                        "mop_clean": {"mop_clean_setting": {"mode_type": "common", "clean_level": "normal"}},
                        "dry_mop_on": {"work_status": "dry_mop", "switch": "on"},
                        "dry_mop_off": {"work_status": "dry_mop", "switch": "off"},
                    }
                },
                "water_tank_setting": {
                    "options": {
                        "low": {"level": "low"},
                        "normal": {"level": "normal"},
                        "high": {"level": "high"}
                    }
                },
            },
            Platform.BINARY_SENSOR: {
                "set_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "translation_key": "disturb"
                },
                "have_reserve_task": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                }
            },
            Platform.SENSOR: {
                "mop": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "sub_work_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "move_direction": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "dust_count": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "area": {
                    "device_class": SensorDeviceClass.AREA,
                    "unit_of_measurement": UnitOfArea.SQUARE_METERS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "switch_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "water_station_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "work_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "battery_percent": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "planner_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "sweep_then_mop_mode_progress": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_desc": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "sweep_mop_mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "work_status": {
                    "device_class": SensorDeviceClass.ENUM,
                }
            }
        }
    },
    "750004AT": {
        "rationale": ["off", "on"],
        "queries": [{"query_type": "work"}],
        "centralized": ["work_status", "battery_percent", "sweep_mop_mode", "mop", "sub_work_status"],
        "entities": {
            Platform.VACUUM: {
                "vacuum": {
                    "control": "work_status",
                    "fan_speeds": {
                        "soft": {"fan_setting": {"level": "soft"}},
                        "normal": {"fan_setting": {"level": "normal"}},
                        "high": {"fan_setting": {"level": "high"}}
                    },
                    "control_actions": {
                        "start": "work",
                        "stop": "stop",
                        "pause": "pause",
                        "return": "charge"
                    }
                }
            },
            Platform.NUMBER: {
                "voice_level": {
                    "min": 1,
                    "max": 100,
                    "step": 1,
                },
            },
            Platform.SELECT: {
                "sweep_mop_mode": {
                    "options": {
                        "sweep_and_mop": {"work_mode_setting": {"work_mode": "sweep_and_mop"}},
                        "sweep": {"work_mode_setting": {"work_mode": "sweep"}},
                        "mop": {"work_mode_setting": {"work_mode": "mop"}},
                        "sweep_then_mop": {"work_mode_setting": {"work_mode": "sweep_then_mop"}}
                    }
                }
            },
            Platform.BINARY_SENSOR: {
                "is_charging": {
                    "device_class": BinarySensorDeviceClass.BATTERY_CHARGING,
                    "on_value": ["charging"],
                    "off_value": ["work", "stop", "pause", "on_base"]
                }
            },
            Platform.SENSOR: {
                "battery_percent": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "area": {
                    "device_class": SensorDeviceClass.AREA,
                    "unit_of_measurement": UnitOfArea.SQUARE_METERS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "work_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "dust_count": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sweep_then_mop_mode_progress": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sub_work_status": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "mop": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "sweep_mop_mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "work_status": {
                    "device_class": SensorDeviceClass.ENUM,
                }
            }
        }
    }
}
