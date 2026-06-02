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
                },
                "buzzer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "self_clean": {
                    "device_class": SwitchDeviceClass.SWITCH,
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
                        "continuity": {"mode": "continuity"},
                        "auto": {"mode": "auto"},
                        "fan": {"mode": "fan"},
                        "dry_shoes": {"mode": "dry_shoes"},
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
                        "comfortable": {"wind_speed": "40"},
                        "high": {"wind_speed": "60"},
                        "turbo": {"wind_speed": "80"},
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
