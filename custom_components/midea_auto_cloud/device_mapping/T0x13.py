from homeassistant.components.fan import DIRECTION_FORWARD, DIRECTION_REVERSE
from homeassistant.const import Platform, UnitOfTemperature, PRECISION_WHOLE

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.LIGHT: {
                "light": {
                    "power": "power",
                    "brightness": {"brightness": [1, 100]},
                    "color_temp": {"color_temperature": [3000, 5700]},  # 添加色温配置
                    "preset_modes": {
                        "night": {"scene_light": "night"},
                        "read": {"scene_light": "read"},
                        "mild": {"scene_light": "mild"},
                        "life": {"scene_light": "life"},
                        "film": {"scene_light": "film"},
                        "manual": {"scene_light": "manual"},
                    }
                }
            }
        }
    },
    "M0200015": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.LIGHT: {
                "light": {
                    "power": "led_power",
                    "brightness": {"brightness": [1, 100]},
                    "color_temp": {"color_temperature": [2700, 6500]},
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
                    "speeds": list({"fan_speed": value + 1} for value in range(0, 6)),
                    "preset_modes": {
                        "breathing_wind": {"fan_scene": "breathing_wind"},
                        "const_temperature": {"fan_scene": "const_temperature"},
                        "fanmanual": {"fan_scene": "fanmanual"},
                        "baby_wind": {"fan_scene": "baby_wind"},
                        "sleep_wind": {"fan_scene": "sleep_wind"},
                        "forest_wind": {"fan_scene": "forest_wind"}
                    }
                }
            }
        }
    },
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
                    "color_temp": {"color_temperature": [2700, 6500]},
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
    }
}
