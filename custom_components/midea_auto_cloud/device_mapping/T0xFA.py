from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE, DEGREE, \
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
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
    },
    "default_fan": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power",
            "gear",
            # 摇头控制：保证切换摇头模式或角度时，control 中不会缺少关键字段
            "lr_shake_switch",
            "ud_shake_switch",
            "lr_angle",
            "ud_angle",
            "lr_diy_angle_down",
            "lr_diy_angle_up",
            "ud_diy_angle_down",
            "ud_diy_angle_up",
            # 双区送风
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
                    "speeds": list({"gear": value + 1} for value in range(0, 100)),
                    "preset_modes": {
                        "double_area": {"mode": "double_area"},
                        "self_selection": {"mode": "self_selection"},
                        "sleeping_wind": {"mode": "sleeping_wind"},
                        "purified_wind": {"mode": "purified_wind"}
                    }
                }
            },
            Platform.SELECT: {
                "swing_angle": {
                    "options": {
                        # 对应 lua：
                        # - normal 模式需要 lr_angle/ud_angle
                        "unknown": {
                            "lr_shake_switch": "off",
                            "ud_shake_switch": "off"
                        },
                        "30": {
                            "lr_shake_switch": "normal",
                            "ud_shake_switch": "normal",
                            "lr_angle": "30",
                            "ud_angle": "30"
                        },
                        "60": {
                            "lr_shake_switch": "normal",
                            "ud_shake_switch": "normal",
                            "lr_angle": "60",
                            "ud_angle": "60"
                        },
                        "90": {
                            "lr_shake_switch": "normal",
                            "ud_shake_switch": "normal",
                            "lr_angle": "90",
                            "ud_angle": "90"
                        },
                        "120": {
                            "lr_shake_switch": "normal",
                            "ud_shake_switch": "normal",
                            "lr_angle": "120",
                            "ud_angle": "120"
                        },
                        "150": {
                            "lr_shake_switch": "normal",
                            "ud_shake_switch": "normal",
                            "lr_angle": "150",
                            "ud_angle": "150"
                        },
                        "180": {
                            "lr_shake_switch": "normal",
                            "ud_shake_switch": "normal",
                            "lr_angle": "180",
                            "ud_angle": "180"
                        }
                    }
                },
                "swing_direction": {
                    "options": {
                        # 对应 lua：通过设置 lr_shake_switch / ud_shake_switch 控制方向
                        "unknown": {
                            "lr_shake_switch": "off",
                            "ud_shake_switch": "off"
                        },
                        "horizontal": {
                            "lr_shake_switch": "normal",
                            "ud_shake_switch": "off"
                        },
                        "vertical": {
                            "lr_shake_switch": "off",
                            "ud_shake_switch": "normal"
                        },
                        "both": {
                            "lr_shake_switch": "normal",
                            "ud_shake_switch": "normal"
                        }
                    }
                },
                "voice": {
                    "options": {
                        "open_buzzer": {"voice": "open_buzzer"},
                        "close_buzzer": {"voice": "close_buzzer"},
                        "mute": {"voice": "mute"}
                    }
                },
                "lr_shake_switch": {
                    "options": {
                        "off": {"lr_shake_switch": "off"},
                        "default": {"lr_shake_switch": "default"},
                        # lua normal 需要 lr_angle
                        "normal": {"lr_shake_switch": "normal"},
                        "diy": {"lr_shake_switch": "diy"},
                    }
                },
                "ud_shake_switch": {
                    "options": {
                        "off": {"ud_shake_switch": "off"},
                        "default": {"ud_shake_switch": "default"},
                        "normal": {"ud_shake_switch": "normal"},
                        # lua diy 需要 ud_diy_angle_down/up
                        "diy": {"ud_shake_switch": "diy"},
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
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "target_angle": {
                    "device_class": SensorDeviceClass.WIND_DIRECTION,
                    "unit_of_measurement": DEGREE,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            },
            Platform.NUMBER: {
                # normal 模式角度
                "lr_angle": {
                    "min": 0,
                    "max": 180,
                    "step": 1,
                    "unit_of_measurement": DEGREE,
                    "default_value": 90
                },
                "ud_angle": {
                    "min": 0,
                    "max": 180,
                    "step": 1,
                    "unit_of_measurement": DEGREE,
                    "default_value": 90
                },
                # diy 模式起始/结束角度
                "lr_diy_angle_down": {
                    "min": 0,
                    "max": 180,
                    "step": 1,
                    "unit_of_measurement": DEGREE
                },
                "lr_diy_angle_up": {
                    "min": 0,
                    "max": 180,
                    "step": 1,
                    "unit_of_measurement": DEGREE
                },
                "ud_diy_angle_down": {
                    "min": 0,
                    "max": 180,
                    "step": 1,
                    "unit_of_measurement": DEGREE
                },
                "ud_diy_angle_up": {
                    "min": 0,
                    "max": 180,
                    "step": 1,
                    "unit_of_measurement": DEGREE
                },
                # 双区送风（area1/area2）
                "area1_time": {
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.SECONDS
                },
                "area2_time": {
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.SECONDS
                },
                "area1_gear": {
                    "min": 0,
                    "max": 26,
                    "step": 1
                },
                "area2_gear": {
                    "min": 0,
                    "max": 26,
                    "step": 1
                },
            }
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
