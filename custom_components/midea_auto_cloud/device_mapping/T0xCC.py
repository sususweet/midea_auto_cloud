from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode.current": "heat"},
                        "cool": {"power": "on", "mode.current": "cool"},
                        "dry": {"power": "on", "mode.current": "dry"},
                        "fan_only": {"power": "on", "mode.current": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco.status": "off",
                            "strong.status": "off",
                            "sterilize.status": "off",
                            "selfclean.status": "off",
                            "humidification.value": "0"
                        },
                        "eco": {"eco.status": "on"},
                        "boost": {"strong.status": "on"},
                        "sterilize": {"sterilize.status": "on"},
                        "selfclean": {"selfclean.status": "on"},
                        "humidify": {"humidification.value": "1"}
                    },
                    "swing_modes": {
                        "off": {"swing.multiple": "false"},
                        "both": {"swing.multiple": "true"},
                        "horizontal": {"swing.louver_horizontal.enable": "true"},
                        "vertical": {"swing.louver_vertical.enable": "true"}
                    },
                    "fan_modes": {
                        "silent": {"wind_speed.level": 1},
                        "low": {"wind_speed.level": 2},
                        "medium": {"wind_speed.level": 3},
                        "high": {"wind_speed.level": 4},
                        "full": {"wind_speed.level": 5},
                        "auto": {"wind_speed.level": 6}
                    },
                    "target_temperature": "temperature.current",
                    "current_temperature": "temperature.room",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "eco": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "eco.status"
                },
                "strong": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "strong.status"
                },
                "selfclean": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "selfclean.status"
                },
                "diagnose": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "diagnose.status"
                },
                "idu_silent": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "idu_silent.status"
                },
                "idu_light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "idu_light"
                },
                "idu_sleep": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "idu_sleep.status"
                },
                "filter_notification": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "filter_notification.status"
                }
            },
            Platform.SENSOR: {
                "room_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "temperature.room"
                },
                "outside_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "temperature.outside"
                },
                "co2_value": {
                    "device_class": SensorDeviceClass.CO2,
                    "unit_of_measurement": "ppm",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "co2.value"
                },
                "hcho_value": {
                    "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                    "unit_of_measurement": "μg/m³",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "hcho.value"
                },
                "pm25_value": {
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": "μg/m³",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "pm2_5.value"
                },
                "wind_speed_level": {
                    "device_class": SensorDeviceClass.ENUM,
                    "attribute": "wind_speed.level"
                },
                "timer_on_timeout": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": "min",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "timer.on.timeout"
                },
                "timer_off_timeout": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": "min",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "timer.off.timeout"
                },
                "selfclean_time_left": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": "min",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "selfclean.time_left"
                },
                "backup_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": "min",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "backup.time"
                },
                "cur_fault_code": {
                    "device_class": SensorDeviceClass.ENUM,
                    "attribute": "cur_fault.code"
                }
            },
            Platform.SELECT: {
                "mode": {
                    "options": {
                        "cool": {"mode.current": "cool"},
                        "dry": {"mode.current": "dry"},
                        "fan": {"mode.current": "fan"},
                        "heat": {"mode.current": "heat"}
                    },
                    "attribute": "mode.current"
                },
                "ptc": {
                    "options": {
                        "auto": {"ptc.status": "auto"},
                        "on": {"ptc.status": "on"},
                        "off": {"ptc.status": "off"},
                        "separate": {"ptc.status": "separate"}
                    },
                    "attribute": "ptc.status"
                },
                "wind_feeling_mode": {
                    "options": {
                        "close": {"wind_feeling.current": "close"},
                        "soft": {"wind_feeling.current": "soft"}
                    },
                    "attribute": "wind_feeling.current"
                },
                "swing_louver": {
                    "options": {
                        "1": {"swing.louver1": "1"},
                        "2": {"swing.louver1": "2"},
                        "3": {"swing.louver1": "3"},
                        "4": {"swing.louver1": "4"},
                        "5": {"swing.louver1": "5"}
                    },
                    "attribute": "swing.louver1"
                },
                "swing_horizontal": {
                    "options": {
                        "1": {"swing.louver_horizontal.level": "1"},
                        "2": {"swing.louver_horizontal.level": "2"},
                        "3": {"swing.louver_horizontal.level": "3"},
                        "4": {"swing.louver_horizontal.level": "4"},
                        "5": {"swing.louver_horizontal.level": "5"}
                    },
                    "attribute": "swing.louver_horizontal.level"
                },
                "swing_vertical": {
                    "options": {
                        "1": {"swing.louver_vertical.level": "1"},
                        "2": {"swing.louver_vertical.level": "2"},
                        "3": {"swing.louver_vertical.level": "3"},
                        "4": {"swing.louver_vertical.level": "4"},
                        "5": {"swing.louver_vertical.level": "5"}
                    },
                    "attribute": "swing.louver_vertical.level"
                }
            }
        }
    }
}
