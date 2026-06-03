from homeassistant.components.humidifier import HumidifierDeviceClass
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform, UnitOfTime

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
                "child_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wind_swing_ud": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "filter_tip": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
            },
            Platform.HUMIDIFIER: {
                "dehumidifier": {
                    "device_class": HumidifierDeviceClass.HUMIDIFIER,
                    "power": "power",
                    "target_humidity": "humidity",
                    "current_humidity": "cur_humidity",
                    "min_humidity": 35,
                    "max_humidity": 85,
                    "mode": "mode",
                    "modes": {
                        "continuity": {"mode": "continuity"},
                        "auto": {"mode": "auto"},
                        "fan": {"mode": "fan"},
                        "dry_shoes": {"mode": "dry_shoes"},
                        "dry_clothes": {"mode": "dry_clothes"}
                    }
                }
            },
            Platform.BINARY_SENSOR: {
                "tank_status": {
                    "device_class": BinarySensorDeviceClass.PROBLEM
                }
            },
            Platform.SELECT: {
                "wind_speed": {
                    "options": {
                        "low": {"wind_speed": "30"},
                        "high": {"wind_speed": "80"},
                    }
                },
                "power_on_time": {
                     "options": {
                        "off": {"power_on_timer": "off"},
                        "15": {"power_on_timer": "on", "power_on_time_value": "15"},
                        "30": {"power_on_timer": "on", "power_on_time_value": "30"},
                        "45": {"power_on_timer": "on", "power_on_time_value": "45"},
                        "60": {"power_on_timer": "on", "power_on_time_value": "60"},
                    }
                },
                "power_off_time": {
                    "options": {
                        "off": {"power_off_timer": "off"},
                        "15": {"power_off_timer": "on", "power_off_time_value": "15"},
                        "30": {"power_off_timer": "on", "power_off_time_value": "30"},
                        "45": {"power_off_timer": "on", "power_off_time_value": "45"},
                        "60": {"power_off_timer": "on", "power_off_time_value": "60"},
                    }
                },
            },
            Platform.SENSOR: {
                "water_full_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_full_level": {
                    "device_class": SensorDeviceClass.ENUM
                },
            }
        }
    },
    "20104032": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "light,sound"}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "anion": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "child_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wind_swing_ud": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "filter_tip": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "purifier": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "sound": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
            },
            Platform.HUMIDIFIER: {
                "dehumidifier": {
                    "device_class": HumidifierDeviceClass.HUMIDIFIER,
                    "power": "power",
                    "target_humidity": "humidity",
                    "current_humidity": "cur_humidity",
                    "mode": "mode",
                    "min_humidity": 35,
                    "max_humidity": 85,
                    "modes": {
                        "set": {"mode": "set"},
                        "continuity": {"mode": "continuity"},
                        "eco": {"mode": "eco"},
                        "dry_clothes": {"mode": "dry_clothes"},
                    },
                },
            },
            Platform.BINARY_SENSOR: {
                "tank_status": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "filter_value": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "water_pump": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "water_pump_enable": {
                },
            },
            Platform.SELECT: {
                "wind_speed": {
                    "options": {
                        "silent": {"wind_speed": "20"},
                        "comfortable": {"wind_speed": "60"},
                        "high": {"wind_speed": "80"},
                        "turbo": {"wind_speed": "100"},
                    },
                },
                "power_on_time": {
                    "options": {
                        "off": {"power_on_timer": "off", "power_on_time_value": 0},
                        "15": {"power_on_timer": "on", "power_on_time_value": 1},
                        "30": {"power_on_timer": "on", "power_on_time_value": 2},
                        "45": {"power_on_timer": "on", "power_on_time_value": 3},
                        "60": {"power_on_timer": "on", "power_on_time_value": 4},
                    },
                },
                "power_off_time": {
                    "options": {
                        "off": {"power_off_timer": "off", "power_off_time_value": 0},
                        "15": {"power_off_timer": "on", "power_off_time_value": 1},
                        "30": {"power_off_timer": "on", "power_off_time_value": 2},
                        "45": {"power_off_timer": "on", "power_off_time_value": 3},
                        "60": {"power_off_timer": "on", "power_off_time_value": 4},
                    },
                },
            },
            Platform.SENSOR: {
                "water_full_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "water_full_level": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "error_code": {
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "version": {
                    "state_class": SensorStateClass.MEASUREMENT,
                },
            },
        },
    },
}
