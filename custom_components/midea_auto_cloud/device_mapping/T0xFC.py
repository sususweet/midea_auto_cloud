from homeassistant.const import Platform, UnitOfTemperature, UnitOfVolume, UnitOfTime, PERCENTAGE, PRECISION_HALVES, \
    UnitOfEnergy, UnitOfPower, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "anion": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "buzzer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "waterions":{
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "mode": {
                    "options": {
                        "constant_humidity": {"mode": "constant_humidity"},
                        "manual": {"mode": "manual"},
                        "sleep": {"mode": "sleep"},
                        "fast": {"mode": "fast"},
                        "auto": {"mode": "auto"},
                    }
                },
                "bias_gear":{
                    "options": {
                        "瑜伽静修场景": {"mode": "auto", "sub_mode": "denoise", "bias_gear": -20},
                        "室内对话场景": {"mode": "auto", "sub_mode": "denoise", "bias_gear": -10}
                    }
                },
                "bright": {
                    "options": {
                        "全亮": {"bright": 0},
                        "半亮": {"bright": 6},
                        "熄灭": {"bright": 7}
                    }
                },
                "gear": {
                    "options": {
                        "low": {"wind_speed": 1},
                        "medium": {"wind_speed": 2},
                        "high": {"wind_speed": 3}
                    }
                },
                "humidity": {
                    "options": {
                        "40%": {"humidity": 40},
                        "50%": {"humidity": 50},
                        "60%": {"humidity": 60},
                        "70%": {"humidity": 70}
                    }
                },
            },
            Platform.SENSOR: {
                "temperature_feedback": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "humidify_feedback": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "hcho":{
                    "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm1":{
                    "device_class": SensorDeviceClass.PM1,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm25":{
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm10":{
                    "device_class": SensorDeviceClass.PM10,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    },
    "571Z3081": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.NUMBER: {
                "hosting_upper": {
                    "min": 10,
                    "max": 75,
                    "step": 1
                },
                "hosting_lower": {
                    "min": 10,
                    "max": 75,
                    "step": 1
                }
            },
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "buzzer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "voice",
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "child_lock",
                },
                "waterions":{
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "mode": {
                    "options": {
                        "manual": {"mode": "manual"},
                        "sleep": {"mode": "sleep"},
                        "auto": {"mode": "auto"},
                        "air_dry": {"mode": "air_dry"}
                    }
                },
                "bias_gear":{
                    "options": {
                        "瑜伽静修场景": {"mode": "auto", "sub_mode": "denoise", "bias_gear": -20},
                        "室内对话场景": {"mode": "auto", "sub_mode": "denoise", "bias_gear": -10}
                    }
                },
                "bright": {
                    "options": {
                        "全亮": {"bright": 0},
                        "半亮": {"bright": 6},
                        "熄灭": {"bright": 7}
                    }
                },
                "gear": {
                    "options": {
                        "low": {"wind_speed": 1},
                        "medium": {"wind_speed": 2},
                        "high": {"wind_speed": 3}
                    }
                }
            },
            Platform.SENSOR: {
                "deep_filter_percent": {
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temperature_feedback": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "humidify_feedback": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "hcho":{
                    "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm1":{
                    "device_class": SensorDeviceClass.PM1,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm25":{
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm10":{
                    "device_class": SensorDeviceClass.PM10,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    },
    "571Z307F": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.NUMBER: {
                "hosting_upper": {
                    "min": 10,
                    "max": 75,
                    "step": 1
                },
                "hosting_lower": {
                    "min": 10,
                    "max": 75,
                    "step": 1
                }
            },
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "buzzer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "voice",
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "child_lock",
                },
                "waterions":{
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "mode": {
                    "options": {
                        "manual": {"mode": "manual"},
                        "sleep": {"mode": "sleep"},
                        "auto": {"mode": "auto"},
                        "fast": {"mode": "fast"}
                    }
                },
                "bright": {
                    "options": {
                        "全亮": {"bright": 0},
                        "半亮": {"bright": 6},
                        "熄灭": {"bright": 7}
                    }
                },
                "gear": {
                    "options": {
                        "low": {"wind_speed": 1},
                        "medium": {"wind_speed": 2},
                        "high": {"wind_speed": 3}
                    }
                },
                "humidity": {
                    "options": {
                        "off": {"humidity": 0},
                        "40%": {"humidity": 40},
                        "50%": {"humidity": 50},
                        "60%": {"humidity": 60}
                    }
                },
            },
            Platform.SENSOR: {
                "deep_filter_percent": {
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temperature_feedback": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "humidify_feedback": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "ash_tvoc":{
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "tvoc_value"
                },
                "pm25":{
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm10":{
                    "device_class": SensorDeviceClass.PM10,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
