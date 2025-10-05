from homeassistant.const import Platform, UnitOfTime, UnitOfArea
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SELECT: {
                "fan_setting": {
                    "options": {
                        "soft": {"level": "soft"},
                        "normal": {"level": "normal"},
                        "high": {"level": "high"},
                        "super": {"level": "super"}
                    }
                },
                "work_mode": {
                    "options": {
                        "sweep_and_mop": {"work_mode": "sweep_and_mop"},
                        "sweep": {"work_mode": "sweep"},
                        "mop": {"work_mode": "mop"},
                        "sweep_then_mop": {"work_mode": "sweep_then_mop"}
                    }
                },
                "work_status": {
                    "options": {
                        "charge": {"work_status": "charge"},
                        "charge_pause": {"work_status": "charge_pause"},
                        "charge_continue": {"work_status": "charge_continue"},
                        "auto_clean": {"work_status": "auto_clean"},
                        "auto_clean_pause": {"work_status": "auto_clean_pause"},
                        "auto_clean_continue": {"work_status": "auto_clean_continue"},
                        "pause": {"work_status": "pause"},
                        "stop": {"work_status": "stop"},
                        "work": {"work_status": "work"},
                        "video_cruise_start": {"work_status": "video_cruise_start"},
                        "video_cruise_pause": {"work_status": "video_cruise_pause"},
                        "quickly_build_map": {"work_status": "quickly_build_map"},
                    }
                },
                "water_tank_setting": {
                    "options": {
                        "low": {"level": "low"},
                        "normal": {"level": "normal"},
                        "high": {"level": "high"}
                    }
                },
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
                "control_type": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "mop_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "sub_work_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "query_type": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "move_direction": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "dust_count": {
                    "device_class": SensorDeviceClass.ENUM
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
                    "device_class": SensorDeviceClass.ENUM
                },
                "water_station_status": {
                    "device_class": SensorDeviceClass.ENUM
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
                    "device_class": SensorDeviceClass.ENUM
                },
                "sweep_then_mop_mode_progress": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_desc": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "station_error_desc": {
                    "device_class": SensorDeviceClass.ENUM
                }
            }
        }
    }
}
