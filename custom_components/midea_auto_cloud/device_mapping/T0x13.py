from homeassistant.components.fan import DIRECTION_FORWARD, DIRECTION_REVERSE
from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PRECISION_WHOLE

# 风扇灯协议（led_power / fan_power，fan_speed 0-100）
# 作为 default，覆盖 M0200015、M0200062 及未单独配置的同系列 SN8
_FAN_LIGHT_MAPPING = {
    "rationale": ["off", "on"],
    "queries": [{}],
    "centralized": [],
    "calculate": {
        "get": [
            {
                "lvalue": "[device_fan_speed]",
                "rvalue": "int((int([fan_speed])) / 20) + 1"
            },
        ],
        "set": [
            {
                "lvalue": "[fan_speed]",
                "rvalue": "min(int((int([device_fan_speed]) - 1) * 20 + 1), 100)"
            },
        ]
    },
    "entities": {
        Platform.LIGHT: {
            "light": {
                "power": "led_power",
                "brightness": {"brightness": [1, 100]},
                "color_temp": {
                    "color_temperature": {
                        "kelvin_range": [2700, 6500],
                        "device_range": [0, 100]
                    }
                },
                "preset_modes": {
                    "work": {"led_scene_light": "work"},
                    "eating": {"led_scene_light": "eating"},
                    "film": {"led_scene_light": "film"},
                    "night": {"led_scene_light": "night"},
                    "ledmanual": {"led_scene_light": "ledmanual"},
                }
            }
        },
        Platform.FAN: {
            "fan": {
                "power": "fan_power",
                "speeds": list({"device_fan_speed": value + 1} for value in range(0, 6)),
                "preset_modes": {
                    "breathing_wind": {"fan_scene": "breathing_wind"},
                    "const_temperature": {"fan_scene": "const_temperature"},
                    "fanmanual": {"fan_scene": "fanmanual"},
                    "baby_wind": {"fan_scene": "baby_wind"},
                    "sleep_wind": {"fan_scene": "sleep_wind"},
                    "forest_wind": {"fan_scene": "forest_wind"}
                },
                "directions": {
                    DIRECTION_FORWARD: {"arround_dir": "1"},
                    DIRECTION_REVERSE: {"arround_dir": "0"},
                },
                # 仅当设备上报 en_oscillating_switch / oscillating_switch 时 fan 实体才展示摆风
                "oscillate": "oscillating_switch",
            }
        }
    }
}

DEVICE_MAPPING = {
    "default": _FAN_LIGHT_MAPPING,
    "79010863": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[device_fan_speed]",
                    "rvalue": "int((int([fan_speed])) / 20) + 1"
                },
            ],
            "set": [
                {
                    "lvalue": "[fan_speed]",
                    "rvalue": "min(int((int([device_fan_speed]) - 1) * 20 + 1), 100)"
                },
            ]
        },
        "entities": {
            Platform.LIGHT: {
                "light": {
                    "power": "led_power",
                    "brightness": {"brightness": [1, 100]},
                    "color_temp": {
                        "color_temperature": {
                            "kelvin_range": [2700, 6500],
                            "device_range": [0, 100]
                        }
                    },
                    "preset_modes": {
                        "work": {"led_scene_light": "work"},
                        "eating": {"led_scene_light": "eating"},
                        "film": {"led_scene_light": "film"},
                        "night": {"led_scene_light": "night"},
                        "ledmanual": {"led_scene_light": "ledmanual"},
                    }
                }
            },
            Platform.FAN: {
                "fan": {
                    "power": "fan_power",
                    "speeds": list({"device_fan_speed": value + 1} for value in range(0, 6)),
                    "preset_modes": {
                        "breathing_wind": {"fan_scene": "breathing_wind"},
                        "const_temperature": {"fan_scene": "const_temperature"},
                        "fanmanual": {"fan_scene": "fanmanual"},
                        "baby_wind": {"fan_scene": "baby_wind"},
                        "sleep_wind": {"fan_scene": "sleep_wind"},
                        "forest_wind": {"fan_scene": "forest_wind"}
                    },
                    "directions": {
                        DIRECTION_FORWARD: {"arround_dir": "1"},
                        DIRECTION_REVERSE: {"arround_dir": "0"},
                    }
                }
            },
            Platform.CLIMATE: {
                 "thermostat": {
                    "power": "fan_power",
                    "hvac_modes": {
                        "off": {"fan_scene": "fanmanual"},
                        "auto": {"fan_scene": "const_temperature"},
                    },
                    "target_temperature": "const_temperature_value",
                    "current_temperature": "indoor_temperature",
                    "min_temp": 20,
                    "max_temp": 35,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_WHOLE,
                }
            }
        }
    },
    # 旧款纯灯：power / scene_light，亮度色温 0-255
    "22222222": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.LIGHT: {
                "light": {
                    "power": "power",
                    "brightness": {"brightness": [0, 255]},
                    "color_temp": {
                        "color_temperature": {
                            "kelvin_range": [2700, 6500],
                            "device_range": [0, 255]
                        }
                    },
                    "preset_modes": {
                        "night": {"scene_light": "night"},
                        "read": {"scene_light": "read"},
                        "mild": {"scene_light": "mild"},
                        "life": {"scene_light": "life"},
                        "film": {"scene_light": "film"},
                        "manual": {"scene_light": "manual"},
                    }
                }
            },
            Platform.NUMBER: {
                "delay_light_off": {
                    "min": 0,
                    "max": 60,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.MINUTES
                }
            }
        }
    }
}
