from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, \
    CONCENTRATION_PARTS_PER_MILLION
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
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
                    "pre_mode": "mode",
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
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
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
                    "unit_of_measurement": CONCENTRATION_PARTS_PER_MILLION,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "co2.value"
                },
                "hcho_value": {
                    "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "hcho.value"
                },
                "pm25_value": {
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
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
    },
    "171PNL01": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode_current": "heat"},
                        "cool": {"power": "on", "mode_current": "cool"},
                        "dry": {"power": "on", "mode_current": "dry"},
                        "fan_only": {"power": "on", "mode_current": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco_status": "off",
                            "sterilize_status": "off",
                            "selfclean_status": "off",
                            "humidification_enable": "false"
                        },
                        "eco": {"eco_status": "on"},
                        "sterilize": {"sterilize_status": "on"},
                        "selfclean": {"selfclean_status": "on"},
                        "humidify": {"humidification_enable": "true"}
                    },
                    "swing_modes": {
                        "off": {"swing_multiple": "false", "swing_louver_horizontal_enable": "false", "swing_louver_vertical_enable": "false"},
                        "both": {"swing_multiple": "true"},
                        "horizontal": {"swing_louver_horizontal_enable": "true"},
                        "vertical": {"swing_louver_vertical_enable": "true"}
                    },
                    "fan_modes": {
                        "1": {"wind_speed_level": "1"},
                        "2": {"wind_speed_level": "2"},
                        "3": {"wind_speed_level": "3"},
                        "4": {"wind_speed_level": "4"},
                        "5": {"wind_speed_level": "5"},
                        "6": {"wind_speed_level": "6"},
                        "7": {"wind_speed_level": "7"},
                        "auto": {"wind_speed_level": "auto"}
                    },
                    "target_temperature": "temperature_current",
                    "current_temperature": "temperature_room",
                    "pre_mode": "mode_current",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "sterilize_status": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "sterilize"
                },
                "eco_status": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "eco"
                },
                "selfclean_status": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "selfclean"
                },
                "idu_silent_status": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "idu_silent"
                },
                "idu_light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "idu_light"
                },
                "idu_sleep_status": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "idu_sleep"
                }
            },
            Platform.SENSOR: {
                "mode_current": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "mode",
                },
                "temperature_room": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "room_temperature"
                },
                "temperature_outside": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "outside_temperature"
                },
                "co2_value": {
                    "device_class": SensorDeviceClass.CO2,
                    "unit_of_measurement": CONCENTRATION_PARTS_PER_MILLION,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "co2_value"
                },
                "wind_speed_level": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "wind_speed_level"
                },
                "selfclean_time_left": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": "min",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "selfclean_time_left"
                },
                "back_up_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "back_up_status"
                },
                "cur_fault_code": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "cur_fault_code"
                }
            },
            Platform.SELECT: {
                "mode_current": {
                    "options": {
                        "cool": {"mode_current": "cool"},
                        "dry": {"mode_current": "dry"},
                        "fan": {"mode_current": "fan"},
                        "heat": {"mode_current": "heat"}
                    },
                    "translation_key": "mode"
                },
                "ptc_status": {
                    "options": {
                        "auto": {"ptc_status": "auto"},
                        "on": {"ptc_status": "on"},
                        "off": {"ptc_status": "off"},
                        "separate": {"ptc_status": "separate"}
                    },
                    "translation_key": "ptc"
                },
                "wind_feeling_current": {
                    "options": {
                        "close": {"wind_feeling_current": "close"},
                        "soft": {"wind_feeling_current": "soft"},
                        "follow": {"wind_feeling_current": "follow"},
                        "avoid": {"wind_feeling_current": "avoid"},
                        "strong": {"wind_feeling_current": "strong"}
                    },
                    "translation_key": "wind_feeling_mode"
                },
                "swing_louver_horizontal_level": {
                    "options": {
                        "1": {"swing_louver_horizontal_level": "1"},
                        "2": {"swing_louver_horizontal_level": "2"},
                        "3": {"swing_louver_horizontal_level": "3"},
                        "4": {"swing_louver_horizontal_level": "4"},
                        "5": {"swing_louver_horizontal_level": "5"},
                        "close": {"swing_louver_horizontal_level": "close"},
                        "auto": {"swing_louver_horizontal_level": "auto"}
                    },
                    "translation_key": "swing_horizontal"
                },
                "swing_louver_vertical_level": {
                    "options": {
                        "1": {"swing_louver_vertical_level": "1"},
                        "2": {"swing_louver_vertical_level": "2"},
                        "3": {"swing_louver_vertical_level": "3"},
                        "4": {"swing_louver_vertical_level": "4"},
                        "5": {"swing_louver_vertical_level": "5"},
                        "close": {"swing_louver_vertical_level": "close"},
                        "auto": {"swing_louver_vertical_level": "auto"}
                    },
                    "translation_key": "swing_vertical"
                }
            }
        }
    },
    "000K86JB": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "run_status"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "dry": {"power": "on", "mode": "dry"},
                        "fan_only": {"power": "on", "mode": "fan"}
                    },
                    "fan_modes": {
                        "power": {"wind_speed": "power"},
                        "super_high": {"wind_speed": "super_high"},
                        "high": {"wind_speed": "high"},
                        "middle": {"wind_speed": "middle"},
                        "low": {"wind_speed": "low"},
                        "micron": {"wind_speed": "micron"},
                        "sleep": {"wind_speed": "sleep"},
                        "auto": {"wind_speed": "auto"}
                    },
                    "target_temperature": "temperature",
                    "current_temperature": "indoor_temperature",
                    "pre_mode": "mode",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "eco": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "wirectrl_child_lock",
                    "rationale": ["wirectrl_child_unlocked", "wirectrl_child_locked"]
                },
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "digit_display_switch"
                },
                "sleep": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "sleep_switch"
                },
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "room_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "indoor_temperature"
                }
            },
            Platform.SELECT: {
                "ptc": {
                    "options": {
                        "on": {"ptc_setting": "ptc_setting_on", "eco":"off"},
                        "off": {"ptc_setting": "ptc_setting_off"},
                    },
                },
                "ud_swing_angle": {
                    "options": {
                        "swing_ud_no_site": {"wind_swing_ud_site": "swing_ud_no_site"},
                        "swing_ud_site_1": {"wind_swing_ud_site": "swing_ud_site_1"},
                        "swing_ud_site_2": {"wind_swing_ud_site": "swing_ud_site_2"},
                        "swing_ud_site_3": {"wind_swing_ud_site": "swing_ud_site_3"},
                        "swing_ud_site_4": {"wind_swing_ud_site": "swing_ud_site_4"},
                        "swing_ud_site_5": {"wind_swing_ud_site": "swing_ud_site_5"},
                        "swing_ud_site_6": {"wind_swing_ud_site": "swing_ud_site_6"},
                    },
                    "attribute": "wind_swing_ud_site"
                },
                "lr_swing_angle": {
                    "options": {
                        "swing_lr_no_site": {"wind_swing_lr_site": "swing_lr_no_site"},
                        "swing_lr_site_1": {"wind_swing_lr_site": "swing_lr_site_1"},
                        "swing_lr_site_2": {"wind_swing_lr_site": "swing_lr_site_2"},
                        "swing_lr_site_3": {"wind_swing_lr_site": "swing_lr_site_3"},
                        "swing_lr_site_4": {"wind_swing_lr_site": "swing_lr_site_4"},
                        "swing_lr_site_5": {"wind_swing_lr_site": "swing_lr_site_5"},
                        "swing_lr_site_6": {"wind_swing_lr_site": "swing_lr_site_6"},
                    },
                    "attribute": "wind_swing_lr_site"
                }
            }
        }
    }
}
