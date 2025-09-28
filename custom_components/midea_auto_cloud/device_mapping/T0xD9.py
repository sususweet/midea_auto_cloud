from homeassistant.const import Platform, UnitOfElectricPotential, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": [0, 1],
        "queries": [{}],
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
            Platform.SWITCH: {
                "db_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_clean_notification": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_softener_needed": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_detergent_needed": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_nightly_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_baby_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_steam_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_fast_clean_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_wash_dry_link": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "db_running_status": {
                    "options": {
                        "stop": {"db_running_status": "stop"},
                        "start": {"db_running_status": "start"},
                        "pause": {"db_running_status": "pause"},
                        "finish": {"db_running_status": "finish"},
                        "error": {"db_running_status": "error"}
                    }
                },
                "db_program": {
                    "options": {
                        "fast_wash_30": {"db_program": "fast_wash_30"},
                        "normal_wash": {"db_program": "normal_wash"},
                        "heavy_wash": {"db_program": "heavy_wash"},
                        "delicate_wash": {"db_program": "delicate_wash"},
                        "quick_wash": {"db_program": "quick_wash"},
                        "eco_wash": {"db_program": "eco_wash"}
                    }
                },
                "db_water_level": {
                    "options": {
                        "low": {"db_water_level": "1"},
                        "medium": {"db_water_level": "2"},
                        "high": {"db_water_level": "3"},
                        "extra_high": {"db_water_level": "4"}
                    }
                },
                "db_temperature": {
                    "options": {
                        "cold": {"db_temperature": "1"},
                        "warm": {"db_temperature": "2"},
                        "hot": {"db_temperature": "3"},
                        "extra_hot": {"db_temperature": "4"}
                    }
                },
                "dehydration_speed": {
                    "options": {
                        "low": {"dehydration_speed": "1"},
                        "medium": {"dehydration_speed": "2"},
                        "high": {"dehydration_speed": "3"},
                        "extra_high": {"dehydration_speed": "4"}
                    }
                },
                "db_detergent": {
                    "options": {
                        "none": {"db_detergent": "1"},
                        "little": {"db_detergent": "2"},
                        "normal": {"db_detergent": "3"},
                        "more": {"db_detergent": "4"}
                    }
                },
                "db_softener": {
                    "options": {
                        "none": {"db_softener": "1"},
                        "little": {"db_softener": "2"},
                        "normal": {"db_softener": "3"},
                        "more": {"db_softener": "4"}
                    }
                },
                "db_position": {
                    "options": {
                        "position_1": {"db_position": "1"},
                        "position_2": {"db_position": "2"},
                        "position_3": {"db_position": "3"}
                    }
                },
                "db_location": {
                    "options": {
                        "location_1": {"db_location": "1"},
                        "location_2": {"db_location": "2"},
                        "location_3": {"db_location": "3"}
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
                "db_device_software_version": {
                    "device_class": SensorDeviceClass.ENUM
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
