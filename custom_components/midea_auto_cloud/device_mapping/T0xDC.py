from homeassistant.const import Platform, UnitOfTime
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
                "control_status": {
                    "rationale": ["pause", "start"],
                },
                "ai_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "prevent_wrinkle_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "steam_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "damp_dry_signal": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "eco_dry_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "bucket_clean_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "water_box": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "baby_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "remind_sound": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "steam": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
            },
            Platform.BINARY_SENSOR: {
                "door_warn": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            },
            Platform.SELECT: {
                "program": {
                    "options": {
                        "cotton": {"program": "cotton"},
                        "fiber": {"program": "fiber"},
                        "mixed_wash": {"program": "mixed_wash"},
                        "jean": {"program": "jean"},
                        "bedsheet": {"program": "bedsheet"},
                        "outdoor": {"program": "outdoor"},
                        "down_jacket": {"program": "down_jacket"},
                        "plush": {"program": "plush"},
                        "wool": {"program": "wool"},
                        "dehumidify": {"program": "dehumidify"},
                        "cold_air_fresh_air": {"program": "cold_air_fresh_air"},
                        "hot_air_dry": {"program": "hot_air_dry"},
                        "sport_clothes": {"program": "sport_clothes"},
                        "underwear": {"program": "underwear"},
                        "baby_clothes": {"program": "baby_clothes"},
                        "shirt": {"program": "shirt"},
                        "standard": {"program": "standard"},
                        "quick_dry": {"program": "quick_dry"},
                        "fresh_air": {"program": "fresh_air"},
                        "low_temp_dry": {"program": "low_temp_dry"},
                        "eco_dry": {"program": "eco_dry"},
                        "quick_dry_30": {"program": "quick_dry_30"},
                        "towel": {"program": "towel"},
                        "intelligent_dry": {"program": "intelligent_dry"},
                        "steam_care": {"program": "steam_care"},
                        "big": {"program": "big"},
                        "fixed_time_dry": {"program": "fixed_time_dry"},
                        "night_dry": {"program": "night_dry"},
                        "bracket_dry": {"program": "bracket_dry"},
                        "western_trouser": {"program": "western_trouser"},
                        "dehumidification": {"program": "dehumidification"},
                        "smart_dry": {"program": "smart_dry"},
                        "four_piece_suit": {"program": "four_piece_suit"},
                        "warm_clothes": {"program": "warm_clothes"},
                        "quick_dry_20": {"program": "quick_dry_20"},
                        "steam_sterilize": {"program": "steam_sterilize"},
                        "enzyme": {"program": "enzyme"},
                        "big_60": {"program": "big_60"},
                        "steam_no_iron": {"program": "steam_no_iron"},
                        "air_wash": {"program": "air_wash"},
                        "bed_clothes": {"program": "bed_clothes"},
                        "little_fast_dry": {"program": "little_fast_dry"},
                        "small_piece_dry": {"program": "small_piece_dry"},
                        "big_dry": {"program": "big_dry"},
                        "wool_nurse": {"program": "wool_nurse"},
                        "sun_quilt": {"program": "sun_quilt"},
                        "fresh_remove_smell": {"program": "fresh_remove_smell"},
                        "bucket_self_clean": {"program": "bucket_self_clean"},
                        "silk": {"program": "silk"},
                        "sterilize": {"program": "sterilize"},
                        "heavy_duty": {"program": "heavy_duty"},
                        "towel_warmer": {"program": "towel_warmer"},
                        "air_fluff": {"program": "air_fluff"},
                        "delicates": {"program": "delicates"},
                        "time_drying_30": {"program": "time_drying_30"},
                        "time_drying_60": {"program": "time_drying_60"},
                        "time_drying_90": {"program": "time_drying_90"},
                        "dry_softnurse": {"program": "dry_softnurse"},
                        "uniforms": {"program": "uniforms"},
                        "remove_electricity": {"program": "remove_electricity"}
                    }
                }
            },
            Platform.SENSOR: {
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
                "progress": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "dry_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
