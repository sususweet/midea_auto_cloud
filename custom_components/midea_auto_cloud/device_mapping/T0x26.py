from homeassistant.const import Platform, UnitOfTemperature, PERCENTAGE, PRECISION_HALVES, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "blowing_direction", "function_led_enable", "smelly_trigger", "subpacket_type",
            "heating_direction", "light_mode", "drying_time", "wifi_led_enable", "mode",
            "night_light_brightness", "bath_heating_time", "bath_direction", "delay_enable",
            "main_light_brightness", "current_temperature", "digit_led_enable", "version",
            "dehumidity_trigger", "delay_time", "bath_temperature", "blowing_speed"
        ],
        "entities": {
            Platform.SWITCH: {
                "function_led_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "smelly_trigger": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wifi_led_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "delay_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "digit_led_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dehumidity_trigger": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "blowing_direction": {
                    "options": {
                        "0": {"blowing_direction": 0},
                        "45": {"blowing_direction": 45},
                        "90": {"blowing_direction": 90},
                        "135": {"blowing_direction": 135},
                        "180": {"blowing_direction": 180},
                        "225": {"blowing_direction": 225},
                        "253": {"blowing_direction": 253}
                    }
                },
                "heating_direction": {
                    "options": {
                        "0": {"heating_direction": 0},
                        "45": {"heating_direction": 45},
                        "90": {"heating_direction": 90},
                        "135": {"heating_direction": 135},
                        "180": {"heating_direction": 180},
                        "225": {"heating_direction": 225},
                        "253": {"heating_direction": 253}
                    }
                },
                "light_mode": {
                    "options": {
                        "close_all": {"light_mode": "close_all"},
                        "night_light": {"light_mode": "night_light"},
                        "main_light": {"light_mode": "main_light"}
                    }
                },
                "mode": {
                    "options": {
                        "close_all": {"mode": "close_all"},
                        "strong_heating": {"mode": "strong_heating"},
                        "weak_heating": {"mode": "weak_heating"},
                        "heating": {"mode": "heating"},
                        "bath": {"mode": "bath"},
                        "soft_wind": {"mode": "soft_wind"},
                        "ventilation": {"mode": "ventilation"},
                        "morning_ventilation": {"mode": "morning_ventilation"},
                        "drying": {"mode": "drying"},
                        "blowing": {"mode": "blowing"},
                        "drying_safe_power": {"mode": "drying_safe_power"},
                        "drying_fast": {"mode": "drying_fast"}
                    }
                },
                "bath_direction": {
                    "options": {
                        "0": {"bath_direction": 0},
                        "45": {"bath_direction": 45},
                        "90": {"bath_direction": 90},
                        "135": {"bath_direction": 135},
                        "180": {"bath_direction": 180},
                        "225": {"bath_direction": 225},
                        "253": {"bath_direction": 253}
                    }
                },
                "drying_direction": {
                    "options": {
                        "0": {"drying_direction": 0},
                        "45": {"drying_direction": 45},
                        "90": {"drying_direction": 90},
                        "135": {"drying_direction": 135},
                        "180": {"drying_direction": 180},
                        "225": {"drying_direction": 225},
                        "253": {"drying_direction": 253}
                    }
                }
            },
            Platform.SENSOR: {
                "drying_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "night_light_brightness": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "bath_heating_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "main_light_brightness": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "current_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "delay_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "bath_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "blowing_speed": {
                    "device_class": SensorDeviceClass.ENUM,
                }
            }
        }
    },
    "M0100040": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.NUMBER: {
                "bath_temperature": {
                    "min": 30,
                    "max": 42,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS
                },
                "heating_temperature": {
                    "min": 30,
                    "max": 42,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS
                },
                "main_light_brightness": {
                    "min": 10,
                    "max": 100,
                    "step": 1,
                    "unit_of_measurement": PERCENTAGE
                },
                "radar_induction_closing_time": {
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.MINUTES
                } 
            },
            Platform.SWITCH: {
                "radar_induction_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wifi_led_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "wind_direction": {
                    "options": {
                        "60": {"heating_direction": "60", "bath_direction": "60", "blowing_direction": "60", "drying_direction": "60"},
                        "70": {"heating_direction": "70", "bath_direction": "70", "blowing_direction": "70", "drying_direction": "70"},
                        "80": {"heating_direction": "80", "bath_direction": "80", "blowing_direction": "80", "drying_direction": "80"},
                        "90": {"heating_direction": "90", "bath_direction": "90", "blowing_direction": "90", "drying_direction": "90"},
                        "100": {"heating_direction": "100", "bath_direction": "100", "blowing_direction": "100", "drying_direction": "100"},
                        "110": {"heating_direction": "110", "bath_direction": "110", "blowing_direction": "110", "drying_direction": "110"},
                        "120": {"heating_direction": "120", "bath_direction": "120", "blowing_direction": "120", "drying_direction": "120"},
                        "swing": {"heating_direction": "253", "bath_direction": "253", "blowing_direction": "253", "drying_direction": "253"}
                    }
                },
                "light_mode": {
                    "options": {
                        "close_all": {"light_mode": "close_all"},
                        "night_light": {"light_mode": "night_light"},
                        "main_light": {"light_mode": "main_light"}
                    }
                },
                "mode": {
                    "options": {
                        "close_all": {"mode": "close_all"},
                        "heating": {"mode": "heating"},
                        "bath": {"mode": "bath"},
                        "blowing": {"mode": "blowing"},
                        "ventilation": {"mode": "ventilation"},
                        "drying": {"mode": "drying"}
                    }
                },
            },
            Platform.SENSOR: {
                "night_light_brightness": {
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "main_light_brightness": {
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "current_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "delay_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
