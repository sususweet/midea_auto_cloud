from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE, DEGREE, \
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

# 新协议：lr/ud_shake_switch（T_0000_FA.lua、56011CBE 等公共部分）
_SHAKE_FAN_MAPPING = {
    "rationale": ["off", "on"],
    "queries": [{}],
    "centralized": [
        "power",
        "gear",
        "lr_shake_switch",
        "ud_shake_switch",
        "lr_diy_angle_down",
        "lr_diy_angle_up",
        "ud_diy_angle_down",
        "ud_diy_angle_up",
        "area1_time",
        "area2_time",
        "area1_gear",
        "area2_gear",
    ],
    "entities": {
        Platform.SWITCH: {
            "display_on_off": {
                "device_class": SwitchDeviceClass.SWITCH,
                "rationale": ["on", "off"]
            },
            "anion": {
                "device_class": SwitchDeviceClass.SWITCH,
            },
            "temp_wind_switch": {
                "device_class": SwitchDeviceClass.SWITCH,
            },
        },
        Platform.FAN: {
            "fan": {
                "power": "power",
                "speeds": list({"gear": value + 1} for value in range(0, 12)),
                # off 关闭；default 为整幅摇头
                "oscillate": "lr_shake_switch",
                "oscillate_rationale": ["off", "default"],
                "preset_modes": {
                    "normal": {"mode": "normal"},
                    "natural": {"mode": "natural"},
                    "sleep": {"mode": "sleep"},
                    "comfort": {"mode": "comfort"},
                    "baby": {"mode": "baby"},
                    "strong": {"mode": "strong"},
                    "self_selection": {"mode": "self_selection"},
                    "sleeping_wind": {"mode": "sleeping_wind"},
                    "ai_smart": {"mode": "ai_smart"},
                    "double_area": {
                        "mode": "double_area",
                        "area1_time": 3,
                        "area2_time": 3,
                        "area1_gear": 1,
                        "area2_gear": 1,
                        "lr_shake_switch": "diy",
                    },
                }
            }
        },
        Platform.SELECT: {
            "lr_shake_switch": {
                "options": {
                    "off": {"lr_shake_switch": "off"},
                    "default": {"lr_shake_switch": "default"},
                    "diy": {"lr_shake_switch": "diy"},
                },
                "translation_key": "lr_swing_angle"
            },
            "ud_shake_switch": {
                "options": {
                    "off": {"ud_shake_switch": "off"},
                    "default": {"ud_shake_switch": "default"},
                    "diy": {"ud_shake_switch": "diy"},
                },
                "translation_key": "ud_swing_angle"
            },
            "voice": {
                "options": {
                    "open_buzzer": {"voice": "open_buzzer"},
                    "close_buzzer": {"voice": "close_buzzer"},
                    "mute": {"voice": "mute"}
                }
            },
        },
        Platform.SENSOR: {
            "real_gear": {
                "device_class": SensorDeviceClass.ENUM,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "dust_life_time": {
                "device_class": SensorDeviceClass.DURATION,
                "unit_of_measurement": UnitOfTime.HOURS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "filter_life_time": {
                "device_class": SensorDeviceClass.DURATION,
                "unit_of_measurement": UnitOfTime.HOURS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "current_angle": {
                "device_class": SensorDeviceClass.WIND_DIRECTION,
                "unit_of_measurement": DEGREE,
                "state_class": SensorStateClass.MEASUREMENT,
                "translation_key": "lr_current_angle"
            },
            "ud_current_angle": {
                "device_class": SensorDeviceClass.WIND_DIRECTION,
                "unit_of_measurement": DEGREE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "temperature_feedback": {
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
                "translation_key": "indoor_temperature"
            }
        },
        Platform.NUMBER: {
            "target_angle": {
                "min": 0,
                "max": 120,
                "step": 1,
                "unit_of_measurement": DEGREE,
                "default_value": 60,
                "translation_key": "lr_target_angle"
            },
            "ud_target_angle": {
                "min": 0,
                "max": 135,
                "step": 1,
                "unit_of_measurement": DEGREE,
                "default_value": 60
            },
            "lr_diy_angle_down": {
                "min": 0,
                "max": 120,
                "step": 1,
                "unit_of_measurement": DEGREE
            },
            "lr_diy_angle_up": {
                "min": 0,
                "max": 120,
                "step": 1,
                "unit_of_measurement": DEGREE
            },
            "ud_diy_angle_down": {
                "min": 0,
                "max": 120,
                "step": 1,
                "unit_of_measurement": DEGREE
            },
            "ud_diy_angle_up": {
                "min": 0,
                "max": 120,
                "step": 1,
                "unit_of_measurement": DEGREE
            },
            "area1_time": {
                "min": 3,
                "max": 10,
                "step": 1,
                "unit_of_measurement": UnitOfTime.SECONDS
            },
            "area2_time": {
                "min": 3,
                "max": 10,
                "step": 1,
                "unit_of_measurement": UnitOfTime.SECONDS
            },
            "area1_gear": {
                "min": 1,
                "max": 12,
                "step": 1
            },
            "area2_gear": {
                "min": 1,
                "max": 12,
                "step": 1
            },
        }
    }
}

# 左右/上下角度选择协议（category=fan 或指定 SN8）
_ANGLE_SELECT_FAN_MAPPING = {
    "rationale": ["off", "on"],
    "queries": [{}],
    "centralized": [
        "power",
        "gear"
    ],
    "entities": {
        Platform.SWITCH: {
            "display_on_off": {
                "device_class": SwitchDeviceClass.SWITCH,
                "rationale": ["on", "off"]
            },
            "waterions": {
                "device_class": SwitchDeviceClass.SWITCH,
            },
        },
        Platform.FAN: {
            "fan": {
                "power": "power",
                "speeds": list({"gear": value + 1} for value in range(0, 9)),
                "preset_modes": {
                    "normal": {"mode": "normal"},
                    "storm": {"mode": "storm"},
                    "self_selection": {"mode": "self_selection"}
                }
            }
        },
        Platform.SELECT: {
            "ud_swing": {
                "options": {
                    "off": {"ud_swing": "off"},
                    "on": {"ud_swing": "on"},
                    "30°": {"ud_swing": 30},
                    "60°": {"ud_swing": 60},
                    "135°": {"ud_swing": 135},
                },
                "translation_key": "ud_swing_angle"
            },
            "lr_swing": {
                "options": {
                    "off": {"lr_swing": "off"},
                    "on": {"lr_swing": "on"},
                    "30°": {"lr_swing": 30},
                    "60°": {"lr_swing": 60},
                    "120°": {"lr_swing": 120},
                },
                "translation_key": "lr_swing_angle"
            },
            "voice": {
                "options": {
                    "open_buzzer": {"voice": "open_buzzer"},
                    "close_buzzer": {"voice": "close_buzzer"},
                    "mute": {"voice": "mute"}
                }
            },
        },
        Platform.SENSOR: {
            "real_gear": {
                "device_class": SensorDeviceClass.ENUM,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "dust_life_time": {
                "device_class": SensorDeviceClass.DURATION,
                "unit_of_measurement": UnitOfTime.HOURS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "filter_life_time": {
                "device_class": SensorDeviceClass.DURATION,
                "unit_of_measurement": UnitOfTime.HOURS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "current_angle": {
                "device_class": SensorDeviceClass.WIND_DIRECTION,
                "unit_of_measurement": DEGREE,
                "state_class": SensorStateClass.MEASUREMENT,
                "translation_key": "lr_current_angle"
            },
            "ud_swing_angle": {
                "device_class": SensorDeviceClass.WIND_DIRECTION,
                "unit_of_measurement": DEGREE,
                "state_class": SensorStateClass.MEASUREMENT
            },
        },
    }
}

# 旧协议：swing on/off（56001177 等）
_LEGACY_SWING_FAN_MAPPING = {
    "rationale": ["off", "on"],
    "queries": [{}],
    "centralized": [
        "power", "swing", "display_on_off", "temp_wind_switch",
    ],
    "entities": {
        Platform.SWITCH: {
            "display_on_off": {
                "device_class": SwitchDeviceClass.SWITCH,
                "rationale": ["on", "off"]
            },
            "temp_wind_switch": {
                "device_class": SwitchDeviceClass.SWITCH,
            },
        },
        Platform.FAN: {
            "fan": {
                "power": "power",
                "speeds": list({"gear": value + 1} for value in range(0, 9)),
                "oscillate": "swing",
                "preset_modes": {
                    "normal": {"mode": "normal"},
                    "sleep": {"mode": "sleep"},
                    "baby": {"mode": "baby"}
                }
            }
        },
        Platform.SELECT: {
            "voice": {
                "options": {
                    "open_buzzer": {"voice": "open_buzzer"},
                    "close_buzzer": {"voice": "close_buzzer"},
                    "mute": {"voice": "mute"}
                }
            },
            "swing_angle": {
                "options": {
                    "unknown": {"swing_angle": "unknown"},
                    "30": {"swing_angle": "30"},
                    "60": {"swing_angle": "60"},
                    "90": {"swing_angle": "90"},
                    "120": {"swing_angle": "120"},
                    "150": {"swing_angle": "150"},
                    "180": {"swing_angle": "180"}
                }
            },
            "swing_direction": {
                "options": {
                    "unknown": {"swing_direction": "unknown"},
                    "horizontal": {"swing_direction": "horizontal"},
                    "vertical": {"swing_direction": "vertical"},
                    "both": {"swing_direction": "both"}
                }
            },
            "sleep_sensor": {
                "options": {
                    "none": {"sleep_sensor": "none"},
                    "light": {"sleep_sensor": "light"},
                    "sound": {"sleep_sensor": "sound"},
                    "both": {"sleep_sensor": "both"}
                }
            },
        },
        Platform.SENSOR: {
            "real_gear": {
                "device_class": SensorDeviceClass.ENUM,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "dust_life_time": {
                "device_class": SensorDeviceClass.DURATION,
                "unit_of_measurement": UnitOfTime.HOURS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "filter_life_time": {
                "device_class": SensorDeviceClass.DURATION,
                "unit_of_measurement": UnitOfTime.HOURS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "temperature_feedback": {
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "water_feedback": {
                "device_class": SensorDeviceClass.ENUM,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "pm25": {
                "device_class": SensorDeviceClass.PM25,
                "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "ud_swing_angle": {
                "device_class": SensorDeviceClass.ENUM,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "lr_diy_down_percent": {
                "device_class": SensorDeviceClass.BATTERY,
                "unit_of_measurement": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "lr_diy_up_percent": {
                "device_class": SensorDeviceClass.BATTERY,
                "unit_of_measurement": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "ud_diy_down_percent": {
                "device_class": SensorDeviceClass.BATTERY,
                "unit_of_measurement": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "ud_diy_up_percent": {
                "device_class": SensorDeviceClass.BATTERY,
                "unit_of_measurement": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT
            }
        }
    }
}

DEVICE_MAPPING = {
    # 新协议公共默认（56011CBE 等同系列）
    "default": _SHAKE_FAN_MAPPING,
    "56011CBE": _SHAKE_FAN_MAPPING,
    # 56011CH9：左右摆风 Select=关闭/30/60/120（对齐美居 App）
    "56011CH9": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power",
            "gear",
            "lr_shake_switch",
            "ud_shake_switch",
            "lr_angle",
            "ud_angle",
            "lr_diy_angle_down",
            "lr_diy_angle_up",
            "ud_diy_angle_down",
            "ud_diy_angle_up",
            "area1_time",
            "area2_time",
            "area1_gear",
            "area2_gear",
        ],
        "entities": {
            Platform.SWITCH: {
                "display_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["on", "off"],
                },
                "anion": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "temp_wind_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.FAN: {
                "fan": {
                    "power": "power",
                    "speeds": list({"gear": value + 1} for value in range(0, 12)),
                    "preset_modes": {
                        "normal": {"mode": "normal"},
                        "natural": {"mode": "natural"},
                        "sleep": {"mode": "sleep"},
                        "comfort": {"mode": "comfort"},
                        "baby": {"mode": "baby"},
                        "strong": {"mode": "strong"},
                        "self_selection": {"mode": "self_selection"},
                        "sleeping_wind": {"mode": "sleeping_wind"},
                        "ai_smart": {"mode": "ai_smart"},
                        "double_area": {
                            "mode": "double_area",
                            "area1_time": 3,
                            "area2_time": 3,
                            "area1_gear": 1,
                            "area2_gear": 1,
                            "lr_shake_switch": "diy",
                        },
                    },
                }
            },
            Platform.SELECT: {
                "lr_shake_switch": {
                    "options": {
                        "off": {"lr_shake_switch": "off"},
                        "30": {"lr_shake_switch": "normal", "lr_angle": "30"},
                        "60": {"lr_shake_switch": "normal", "lr_angle": "60"},
                        "120": {"lr_shake_switch": "normal", "lr_angle": "120"},
                    },
                    "translation_key": "lr_swing_angle",
                },
                "ud_shake_switch": {
                    "options": {
                        "off": {"ud_shake_switch": "off"},
                        "default": {"ud_shake_switch": "default"},
                        "normal": {"ud_shake_switch": "normal"},
                        "diy": {"ud_shake_switch": "diy"},
                    },
                    "translation_key": "ud_swing_angle",
                },
                "voice": {
                    "options": {
                        "open_buzzer": {"voice": "open_buzzer"},
                        "close_buzzer": {"voice": "close_buzzer"},
                        "mute": {"voice": "mute"},
                    }
                },
            },
            Platform.SENSOR: {
                "real_gear": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "dust_life_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "filter_life_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "current_angle": {
                    "device_class": SensorDeviceClass.WIND_DIRECTION,
                    "unit_of_measurement": DEGREE,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "lr_current_angle",
                },
                "ud_current_angle": {
                    "device_class": SensorDeviceClass.WIND_DIRECTION,
                    "unit_of_measurement": DEGREE,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "temperature_feedback": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "indoor_temperature",
                },
            },
            Platform.NUMBER: {
                "lr_diy_angle_down": {
                    "min": 0,
                    "max": 120,
                    "step": 1,
                    "unit_of_measurement": DEGREE,
                },
                "lr_diy_angle_up": {
                    "min": 0,
                    "max": 120,
                    "step": 1,
                    "unit_of_measurement": DEGREE,
                },
                "ud_diy_angle_down": {
                    "min": 0,
                    "max": 120,
                    "step": 1,
                    "unit_of_measurement": DEGREE,
                },
                "ud_diy_angle_up": {
                    "min": 0,
                    "max": 120,
                    "step": 1,
                    "unit_of_measurement": DEGREE,
                },
                "area1_time": {
                    "min": 3,
                    "max": 10,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                },
                "area2_time": {
                    "min": 3,
                    "max": 10,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                },
                "area1_gear": {
                    "min": 1,
                    "max": 12,
                    "step": 1,
                },
                "area2_gear": {
                    "min": 1,
                    "max": 12,
                    "step": 1,
                },
            },
        },
    },

    # category=fan 回退，以及已知角度选择协议 SN8
    "default_fan": _ANGLE_SELECT_FAN_MAPPING,
    ("56011C99", "56011C8T"): _ANGLE_SELECT_FAN_MAPPING,

    # 旧 swing 协议
    ("56001177",): _LEGACY_SWING_FAN_MAPPING,
    # Pelonis FG25-25TSW (560001F4)：左右摇为 on/off；上下为 off/default/固定角度
    "560001F4": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power",
            "gear",
            "mode",
            "lr_shake_switch",
            "ud_shake_switch",
            "ud_angle",
        ],
        "entities": {
            Platform.SWITCH: {
                "display_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["on", "off"],
                    "translation_key": "screen_close",
                },
                "temp_wind_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "auto_power_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "voice": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "voice",
                    "rationale": ["close_buzzer", "open_buzzer"],
                },
            },
            Platform.FAN: {
                "fan": {
                    "power": "power",
                    # 1–9 档；HA Fan 仍以百分比展示，步进对应档位
                    "speeds": list({"gear": value + 1} for value in range(0, 9)),
                    "oscillate": "lr_shake_switch",
                    "oscillate_rationale": ["off", "on"],
                    "preset_modes": {
                        "normal": {"mode": "normal"},
                        "natural": {"mode": "natural"},
                        "sleep": {"mode": "sleep"},
                        "comfort": {"mode": "comfort"},
                        "mute": {"mode": "mute"},
                        "baby": {"mode": "baby"},
                    },
                }
            },
            Platform.SELECT: {
                # 上下摇头：关闭 / 默认幅面 / 30°·60°·135°
                "ud_swing_angle": {
                    "options": {
                        "off": {"ud_shake_switch": "off"},
                        "default": {"ud_shake_switch": "default"},
                        "30": {"ud_shake_switch": "normal", "ud_angle": 30},
                        "60": {"ud_shake_switch": "normal", "ud_angle": 60},
                        "135": {"ud_shake_switch": "normal", "ud_angle": 135},
                    },
                    "translation_key": "ud_swing_angle",
                },
            },
            Platform.SENSOR: {
                "real_gear": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "gear": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
            },
        },
    },
    "BGF10000": {  # BGF10000
        "rationale": ["off", "on"],
        "queries": [{}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[timer_off]",
                    "rvalue": "[timer_off_hour] * 60 + [timer_off_minute]"
                },
                {
                    "lvalue": "[timer_on]",
                    "rvalue": "[timer_on_hour] * 60 + [timer_on_minute]"
                }
            ],
            "set": []
        },
        "centralized": [
            "power",
            "gear"
        ],
        "entities": {
            Platform.LOCK: {
                "lock": {
                    "translation_key": "child_lock",
                },
            },
            Platform.SWITCH: {
                "display_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["on", "off"]
                },
                "temp_wind_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "swing": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.FAN: {
                "fan": {
                    "power": "power",
                    "speeds": list({"gear": value + 1} for value in range(0, 12)),
                    "preset_modes": {
                        "normal": {"mode": "normal"},
                        "comfort": {"mode": "comfort"},
                        "sleep": {"mode": "sleep"},
                        "strong": {"mode": "strong"}
                    }
                }
            },
            Platform.SELECT: {
                "voice": {
                    "options": {
                        "open_buzzer": {"voice": "open_buzzer"},
                        "close_buzzer": {"voice": "close_buzzer"},
                        "mute": {"voice": "mute"}
                    }
                },
            },
            Platform.SENSOR: {
                "timer_off": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "timer_off_minute"
                },
                "timer_on": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "timer_on_minute"
                },
            },
        }
    },
    "5600119Z": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "display_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["on", "off"],
                    "translation_key": "screen_close",
                },
                "humidify": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["off", "1"],
                },
                "waterions": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "anion",
                }
            },
            Platform.FAN: {
                "fan": {
                    "power": "power",
                    "speeds": list({"gear": value + 1} for value in range(0, 3)),
                    "oscillate": "swing",
                    "preset_modes": {
                        "normal": {
                            "mode": "normal",
                            "speeds": list({"gear": value + 1} for value in range(0, 3))
                        },
                        "sleep": {
                            "mode": "sleep",
                            "speeds": list({"gear": value + 1} for value in range(0, 2))
                        },
                        "baby": {
                            "mode": "baby",
                            "speeds": list({"gear": value + 1} for value in range(0, 1))
                        }
                    }
                }
            },
            Platform.SENSOR: {
                "water_feedback": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
