from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime
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
                "subpacket_type": {
                    "device_class": SensorDeviceClass.ENUM,
                },
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
    }
}
