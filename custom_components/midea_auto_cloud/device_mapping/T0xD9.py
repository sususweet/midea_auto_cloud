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
                        "baby_clothes": {"db_program": "baby_clothes"},
                        "baby_clothes_dry": {"db_program": "151"},
                        "clean_stains": {"db_program": "clean_stains"},
                        "cold_wash": {"db_program": "cold_wash"},
                        "cook_wash": {"db_program": "cook_wash"},
                        "fast_wash": {"db_program": "137"},
                        "hot_wind_dry": {"db_program": "153"},
                        "rinsing_dehydration": {"db_program": "rinsing_dehydration"},
                        "self_wash_5": {"db_program": "self_wash_5"},
                        "single_dehytration": {"db_program": "single_dehytration"},
                        "single_drying": {"db_program": "single_drying"},
                        "small_wash_dry": {"db_program": "138"},
                        "socks": {"db_program": "148"},
                        "standard": {"db_program": "standard"},
                        "underpants": {"db_program": "156"},
                        "underwear": {"db_program": "underwear"},
                        "water_ssp": {"db_program": "water_ssp"}
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
