from homeassistant.const import Platform, UnitOfElectricPotential, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[remaining_time]",
                    "rvalue": "[remain_time]"
                }
            ],
            "set": {
            }
        },
        "entities": {
            Platform.BINARY_SENSOR: {
                "softener_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "detergent_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "door_opened": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "bucket_water_overheating": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
            },
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "control_status": {
                    "rationale": ["pause", "start"],
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "flocks_switcher": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ultraviolet_lamp": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["0", "1"],
                },
                "eye_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["0", "1"],
                },
                "microbubble": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["0", "1"],
                },
                "wind_dispel": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["0", "1"],
                },
                "cycle_memory": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SELECT: {
                "dehydration_speed": {
                    "options": {
                        "0": {"dehydration_speed": "0"},
                        "400": {"dehydration_speed": "400"},
                        "600": {"dehydration_speed": "600"},
                        "800": {"dehydration_speed": "800"},
                        "1000": {"dehydration_speed": "1000"},
                        "1200": {"dehydration_speed": "1200"},
                        "1400": {"dehydration_speed": "1400"},
                        "1600": {"dehydration_speed": "1600"},
                        "1300": {"dehydration_speed": "1300"}
                    }
                },
                "mode": {
                    "options": {
                        "normal": {"mode": "normal"},
                        "factory_test": {"mode": "factory_test"},
                        "service": {"mode": "service"},
                        "normal_continus": {"mode": "normal_continus"}
                    }
                },
                "water_level": {
                    "options": {
                        "low": {"water_level": "low"},
                        "medium": {"water_level": "mid"},
                        "high": {"water_level": "high"},
                        "auto": {"water_level": "auto"}
                    }
                },
                "program": {
                    "options": {
                        "cotton": {"program": "cotton"},
                        "eco": {"program": "eco"},
                        "fast_wash": {"program": "fast_wash"},
                        "mixed_wash": {"program": "mixed_wash"},
                        "wool": {"program": "wool"},
                        "ssp": {"program": "ssp"},
                        "sport_clothes": {"program": "sport_clothes"},
                        "single_dehytration": {"program": "single_dehytration"},
                        "rinsing_dehydration": {"program": "rinsing_dehydration"},
                        "big": {"program": "big"},
                        "baby_clothes": {"program": "baby_clothes"},
                        "down_jacket": {"program": "down_jacket"},
                        "color": {"program": "color"},
                        "intelligent": {"program": "intelligent"},
                        "quick_wash": {"program": "quick_wash"},
                        "shirt": {"program": "shirt"},
                        "fiber": {"program": "fiber"},
                        "enzyme": {"program": "enzyme"},
                        "underwear": {"program": "underwear"},
                        "outdoor": {"program": "outdoor"},
                        "air_wash": {"program": "air_wash"},
                        "single_drying": {"program": "single_drying"},
                        "steep": {"program": "steep"},
                        "kids": {"program": "kids"},
                        "water_cotton": {"program": "water_cotton"},
                        "fast_wash_30": {"program": "fast_wash_30"},
                        "fast_wash_60": {"program": "fast_wash_60"},
                        "water_mixed_wash": {"program": "water_mixed_wash"},
                        "water_fiber": {"program": "water_fiber"},
                        "water_kids": {"program": "water_kids"},
                        "water_underwear": {"program": "water_underwear"},
                        "specialist": {"program": "specialist"},
                        "love": {"program": "love"},
                        "water_intelligent": {"program": "water_intelligent"},
                        "water_steep": {"program": "water_steep"},
                        "water_fast_wash_30": {"program": "water_fast_wash_30"},
                        "new_water_cotton": {"program": "new_water_cotton"},
                        "water_eco": {"program": "water_eco"},
                        "wash_drying_60": {"program": "wash_drying_60"},
                        "self_wash_5": {"program": "self_wash_5"},
                        "fast_wash_min": {"program": "fast_wash_min"},
                        "mixed_wash_min": {"program": "mixed_wash_min"},
                        "dehydration_min": {"program": "dehydration_min"},
                        "self_wash_min": {"program": "self_wash_min"},
                        "baby_clothes_min": {"program": "baby_clothes_min"},
                        "diy0": {"program": "diy0"},
                        "diy1": {"program": "diy1"},
                        "diy2": {"program": "diy2"},
                        "silk_wash": {"program": "silk_wash"},
                        "prevent_allergy": {"program": "prevent_allergy"},
                        "cold_wash": {"program": "cold_wash"},
                        "soft_wash": {"program": "soft_wash"},
                        "remove_mite_wash": {"program": "remove_mite_wash"},
                        "water_intense_wash": {"program": "water_intense_wash"},
                        "fast_dry": {"program": "fast_dry"},
                        "water_outdoor": {"program": "water_outdoor"},
                        "spring_autumn_wash": {"program": "spring_autumn_wash"},
                        "summer_wash": {"program": "summer_wash"},
                        "winter_wash": {"program": "winter_wash"},
                        "jean": {"program": "jean"},
                        "new_clothes_wash": {"program": "new_clothes_wash"},
                        "silk": {"program": "silk"},
                        "insight_wash": {"program": "insight_wash"},
                        "fitness_clothes": {"program": "fitness_clothes"},
                        "mink": {"program": "mink"},
                        "fresh_air": {"program": "fresh_air"},
                        "bucket_dry": {"program": "bucket_dry"},
                        "jacket": {"program": "jacket"},
                        "bath_towel": {"program": "bath_towel"},
                        "night_fresh_wash": {"program": "night_fresh_wash"},
                        "heart_wash": {"program": "heart_wash"},
                        "water_cold_wash": {"program": "water_cold_wash"},
                        "water_prevent_allergy": {"program": "water_prevent_allergy"},
                        "water_remove_mite_wash": {"program": "water_remove_mite_wash"},
                        "water_ssp": {"program": "water_ssp"},
                        "standard": {"program": "standard"},
                        "green_wool": {"program": "green_wool"},
                        "cook_wash": {"program": "cook_wash"},
                        "fresh_remove_wrinkle": {"program": "fresh_remove_wrinkle"},
                        "steam_sterilize_wash": {"program": "steam_sterilize_wash"},
                        "aromatherapy": {"program": "aromatherapy"},
                        "sterilize_wash": {"program": "sterilize_wash"},
                        "white_clothes_clean": {"program": "white_clothes_clean"},
                        "clean_stains": {"program": "clean_stains"},
                        "tube_clean_all": {"program": "tube_clean_all"},
                        "no_channeling_color": {"program": "no_channeling_color"},
                        "scald_wash": {"program": "scald_wash"},
                        "hanfu_spring_summer": {"program": "hanfu_spring_summer"},
                        "hanfu_autumn_winter": {"program": "hanfu_autumn_winter"},
                        "skin_care_wash": {"program": "skin_care_wash"},
                        "hanfu_wash": {"program": "hanfu_wash"}
                    }
                },
                "temperature": {
                    "options": {
                        "0": {"temperature": "0"},
                        "20": {"temperature": "20"},
                        "30": {"temperature": "30"},
                        "40": {"temperature": "40"},
                        "50": {"temperature": "50"},
                        "60": {"temperature": "60"},
                        "70": {"temperature": "70"},
                        "90": {"temperature": "90"},
                        "95": {"temperature": "95"}
                    }
                },
                "detergent": {
                    "options": {
                        "0": {"detergent": "0"},
                        "1": {"detergent": "1"},
                        "2": {"detergent": "2"},
                        "3": {"detergent": "3"},
                        "4": {"detergent": "4"},
                        "5": {"detergent": "5"}
                    }
                },
                "softener": {
                    "options": {
                        "0": {"softener": "0"},
                        "1": {"softener": "1"},
                        "2": {"softener": "2"},
                        "3": {"softener": "3"},
                        "4": {"softener": "4"},
                        "5": {"softener": "5"}
                    }
                },
                "dirty_degree": {
                    "options": {
                        "0": {"dirty_degree": "0"},
                        "1": {"dirty_degree": "1"},
                        "2": {"dirty_degree": "2"},
                        "3": {"dirty_degree": "3"},
                        "4": {"dirty_degree": "4"}
                    }
                },
                "soak_count": {
                    "options": {
                        "0": {"soak_count": "0"},
                        "1": {"soak_count": "1"},
                        "2": {"soak_count": "2"},
                        "3": {"soak_count": "3"},
                        "4": {"soak_count": "4"},
                        "5": {"soak_count": "5"}
                    }
                }
            },
            Platform.SENSOR: {
                "running_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "wash_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "appointment_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "remain_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "dryer": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "remote_control_flag": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "progress": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "dehydration_time_value": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "customize_machine_cycle": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "detergent_global": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "softener_global": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "detergent_density_global": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "softener_density_global": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "fresh_air_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "flocks_remind_period": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "expert_step": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "flocks_wash_count": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "active_oxygen": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "dehydration_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai_time2": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "wash_time_value": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
