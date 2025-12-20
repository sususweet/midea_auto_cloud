from homeassistant.const import Platform, UnitOfElectricPotential, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{"query_type": "db"}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[remaining_time]",
                    "rvalue": "[db_remain_time]"
                }
            ],
            "set": {
            }
        },
        "entities": {
            Platform.BINARY_SENSOR: {
                "db_power": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
            },
            Platform.SWITCH: {
                "db_clean_notification": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "db_baby_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "db_light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "db_steam_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "db_fast_clean_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "db_wash_dry_link": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                }
            },
            Platform.SELECT: {
                "db_location_selection": {
                    "options": {
                        "left": {"db_location_selection": "left"},
                        "right": {"db_location_selection": "right"}
                    }
                },
                "db_running_status": {
                    "options": {
                        "off": {"db_power": "off", "db_running_status": "off"},
                        "standby": {"db_power": "on", "db_running_status": "standby"},
                        "start": {"db_power": "on", "db_running_status": "start"},
                        "pause": {"db_power": "on", "db_running_status": "pause"},
                        "end": {"db_power": "on", "db_running_status": "end"},
                        "fault": {"db_power": "on", "db_running_status": "fault"},
                        "delay": {"db_power": "on", "db_running_status": "delay"}
                    }
                },
                "db_program": {
                    "options": {
                        "cotton": {"db_program": "cotton"},
                        "eco": {"db_program": "eco"},
                        "fast_wash": {"db_program": "fast_wash"},
                        "mixed_wash": {"db_program": "mixed_wash"},
                        "wool": {"db_program": "wool"},
                        "ssp": {"db_program": "ssp"},
                        "sport_clothes": {"db_program": "sport_clothes"},
                        "single_dehytration": {"db_program": "single_dehytration"},
                        "rinsing_dehydration": {"db_program": "rinsing_dehydration"},
                        "big": {"db_program": "big"},
                        "baby_clothes": {"db_program": "baby_clothes"},
                        "down_jacket": {"db_program": "down_jacket"},
                        "color": {"db_program": "color"},
                        "intelligent": {"db_program": "intelligent"},
                        "quick_wash": {"db_program": "quick_wash"},
                        "shirt": {"db_program": "shirt"},
                        "fiber": {"db_program": "fiber"},
                        "enzyme": {"db_program": "enzyme"},
                        "underwear": {"db_program": "underwear"},
                        "outdoor": {"db_program": "outdoor"},
                        "air_wash": {"db_program": "air_wash"},
                        "single_drying": {"db_program": "single_drying"},
                        "steep": {"db_program": "steep"},
                        "kids": {"db_program": "kids"},
                        "water_baby_clothes": {"db_program": "water_baby_clothes"},
                        "fast_wash_30": {"db_program": "fast_wash_30"},
                        "water_shirt": {"db_program": "water_shirt"},
                        "water_mixed_wash": {"db_program": "water_mixed_wash"},
                        "water_fiber": {"db_program": "water_fiber"},
                        "water_kids": {"db_program": "water_kids"},
                        "water_underwear": {"db_program": "water_underwear"},
                        "specialist": {"db_program": "specialist"},
                        "love": {"db_program": "love"},
                        "water_intelligent": {"db_program": "water_intelligent"},
                        "water_steep": {"db_program": "water_steep"},
                        "water_fast_wash_30": {"db_program": "water_fast_wash_30"},
                        "new_water_cotton": {"db_program": "new_water_cotton"},
                        "water_eco": {"db_program": "water_eco"},
                        "wash_drying_60": {"db_program": "wash_drying_60"},
                        "self_wash_5": {"db_program": "self_wash_5"},
                        "fast_wash_min": {"db_program": "fast_wash_min"},
                        "mixed_wash_min": {"db_program": "mixed_wash_min"},
                        "dehydration_min": {"db_program": "dehydration_min"},
                        "self_wash_min": {"db_program": "self_wash_min"},
                        "baby_clothes_min": {"db_program": "baby_clothes_min"},
                        "silk_wash": {"db_program": "silk_wash"},
                        "prevent_allergy": {"db_program": "prevent_allergy"},
                        "cold_wash": {"db_program": "cold_wash"},
                        "soft_wash": {"db_program": "soft_wash"},
                        "remove_mite_wash": {"db_program": "remove_mite_wash"},
                        "water_intense_wash": {"db_program": "water_intense_wash"},
                        "fast_dry": {"db_program": "fast_dry"},
                        "water_outdoor": {"db_program": "water_outdoor"},
                        "spring_autumn_wash": {"db_program": "spring_autumn_wash"},
                        "summer_wash": {"db_program": "summer_wash"},
                        "winter_wash": {"db_program": "winter_wash"},
                        "jean": {"db_program": "jean"},
                        "new_clothes_wash": {"db_program": "new_clothes_wash"},
                        "silk": {"db_program": "silk"},
                        "insight_wash": {"db_program": "insight_wash"},
                        "fitness_clothes": {"db_program": "fitness_clothes"},
                        "mink": {"db_program": "mink"},
                        "fresh_air": {"db_program": "fresh_air"},
                        "bucket_dry": {"db_program": "bucket_dry"},
                        "jacket": {"db_program": "jacket"},
                        "bath_towel": {"db_program": "bath_towel"},
                        "night_fresh_wash": {"db_program": "night_fresh_wash"},
                        "degerm": {"db_program": "degerm"},
                        "heart_wash": {"db_program": "heart_wash"},
                        "water_cold_wash": {"db_program": "water_cold_wash"},
                        "water_prevent_allergy": {"db_program": "water_prevent_allergy"},
                        "water_remove_mite_wash": {"db_program": "water_remove_mite_wash"},
                        "water_ssp": {"db_program": "water_ssp"},
                        "standard": {"db_program": "standard"},
                        "green_wool": {"db_program": "green_wool"},
                        "cook_wash": {"db_program": "cook_wash"},
                        "fresh_remove_wrinkle": {"db_program": "fresh_remove_wrinkle"},
                        "steam_sterilize_wash": {"db_program": "steam_sterilize_wash"},
                        "sterilize_wash": {"db_program": "sterilize_wash"},
                        "white_clothes_clean": {"db_program": "white_clothes_clean"},
                        "clean_stains": {"db_program": "clean_stains"},
                        "prevent_cross_color": {"db_program": "prevent_cross_color"},
                        "quick_dry_clothes": {"db_program": "quick_dry_clothes"},
                        "yoga_clothes": {"db_program": "yoga_clothes"}
                    }
                }
            },
            Platform.SENSOR: {
                "db_remain_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_progress": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "db_set_dewater_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_set_wash_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_rinse_count": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "db_wash_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_appointment_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_appointment": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "db_dehydration_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_cycle_memory": {
                    "device_class": SensorDeviceClass.ENUM
                }
            }
        }
    }
}
