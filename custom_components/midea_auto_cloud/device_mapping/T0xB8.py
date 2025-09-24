from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime, UnitOfArea, UnitOfVolume
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SELECT: {
                "fan_level": {
                    "options": {
                        "low": {"fan_level": "low"},
                        "medium": {"fan_level": "medium"},
                        "high": {"fan_level": "high"},
                        "auto": {"fan_level": "auto"}
                    }
                },
                "work_mode": {
                    "options": {
                        "none": {"work_mode": "none"},
                        "auto": {"work_mode": "auto"},
                        "spot": {"work_mode": "spot"},
                        "edge": {"work_mode": "edge"},
                        "single_room": {"work_mode": "single_room"},
                        "custom": {"work_mode": "custom"}
                    }
                },
                "work_status": {
                    "options": {
                        "idle": {"work_status": "idle"},
                        "cleaning": {"work_status": "cleaning"},
                        "returning": {"work_status": "returning"},
                        "docked": {"work_status": "docked"},
                        "on_base": {"work_status": "on_base"},
                        "charging": {"work_status": "charging"},
                        "error": {"work_status": "error"}
                    }
                },
                "move_direction": {
                    "options": {
                        "none": {"move_direction": "none"},
                        "forward": {"move_direction": "forward"},
                        "backward": {"move_direction": "backward"},
                        "left": {"move_direction": "left"},
                        "right": {"move_direction": "right"}
                    }
                },
                "query_type": {
                    "options": {
                        "work": {"query_type": "work"},
                        "status": {"query_type": "status"},
                        "battery": {"query_type": "battery"},
                        "error": {"query_type": "error"}
                    }
                },
                "sub_work_status": {
                    "options": {
                        "idle": {"sub_work_status": "idle"},
                        "cleaning": {"sub_work_status": "cleaning"},
                        "charging": {"sub_work_status": "charging"},
                        "charge_finish": {"sub_work_status": "charge_finish"},
                        "error": {"sub_work_status": "error"}
                    }
                },
                "water_level": {
                    "options": {
                        "low": {"water_level": "low"},
                        "normal": {"water_level": "normal"},
                        "high": {"water_level": "high"}
                    }
                },
                "mop_status": {
                    "options": {
                        "normal": {"mop_status": "normal"},
                        "lack_water": {"mop_status": "lack_water"},
                        "full_water": {"mop_status": "full_water"}
                    }
                },
                "error_type": {
                    "options": {
                        "no_error": {"error_type": "no_error"},
                        "can_fix": {"error_type": "can_fix"},
                        "need_help": {"error_type": "need_help"}
                    }
                },
                "control_type": {
                    "options": {
                        "none": {"control_type": "none"},
                        "app": {"control_type": "app"},
                        "remote": {"control_type": "remote"},
                        "auto": {"control_type": "auto"}
                    }
                }
            },
            Platform.BINARY_SENSOR: {
                "carpet_switch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "have_reserve_task": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                }
            },
            Platform.SENSOR: {
                "dust_count": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "area": {
                    "device_class": SensorDeviceClass.AREA,
                    "unit_of_measurement": UnitOfArea.SQUARE_METERS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "voice_level": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "switch_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_station_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "work_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "battery_percent": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "planner_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sweep_then_mop_mode_progress": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_desc": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "station_error_desc": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
