from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power", "humidify", "swing", "anion", "display_on_off", 
            "dust_reset", "temp_wind_switch", "filter_reset"
        ],
        "entities": {
            Platform.BINARY_SENSOR: {
                "power": {
                    "device_class": BinarySensorDeviceClass.POWER,
                },
                "humidify": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "swing": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "anion": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "display_on_off": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "dust_reset": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "temp_wind_switch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "filter_reset": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
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
                "scene": {
                    "options": {
                        "none": {"scene": "none"},
                        "auto": {"scene": "auto"},
                        "sleep": {"scene": "sleep"},
                        "work": {"scene": "work"},
                        "study": {"scene": "study"},
                        "party": {"scene": "party"}
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
                "mode": {
                    "options": {
                        "normal": {"mode": "normal"},
                        "auto": {"mode": "auto"},
                        "manual": {"mode": "manual"},
                        "sleep": {"mode": "sleep"},
                        "turbo": {"mode": "turbo"},
                        "quiet": {"mode": "quiet"}
                    }
                },
                "gear": {
                    "options": {
                        "1": {"gear": "1"},
                        "2": {"gear": "2"},
                        "3": {"gear": "3"},
                        "4": {"gear": "4"},
                        "5": {"gear": "5"},
                        "6": {"gear": "6"},
                        "auto": {"gear": "auto"}
                    }
                }
            },
            Platform.SENSOR: {
                "real_gear": {
                    "device_class": SensorDeviceClass.NONE,
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
                "battery_status": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "battery_level": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_code": {
                    "device_class": SensorDeviceClass.NONE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temperature_feedback": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_feedback": {
                    "device_class": SensorDeviceClass.NONE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "timer_off_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "timer_off_minute": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "timer_on_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "timer_on_minute": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "version": {
                    "device_class": SensorDeviceClass.NONE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm25": {
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": "µg/m³",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "ud_swing_angle": {
                    "device_class": SensorDeviceClass.NONE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "lr_diy_down_percent": {
                    "device_class": SensorDeviceClass.NONE,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "lr_diy_up_percent": {
                    "device_class": SensorDeviceClass.NONE,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "ud_diy_down_percent": {
                    "device_class": SensorDeviceClass.NONE,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "ud_diy_up_percent": {
                    "device_class": SensorDeviceClass.NONE,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
