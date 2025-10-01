from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "left_power", "left_recipe_current_step_action", "left_recipe_id",
            "left_dry_fire_protection", "left_recipe_rest_time", "left_gear",
            "left_current_temperature", "lock", "left_status", "eq_recipe_action",
            "left_lock", "gas_leakage_code", "left_work_time", "left_recipe_current_step",
            "left_recipe_target_steps", "version", "left_recipe_target_time",
            "is_error", "left_cookmode", "light_lampblack_mode", "error_type"
        ],
        "entities": {
            Platform.SWITCH: {
                "left_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "left_dry_fire_protection": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "left_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ['0', '1'],
                },
                "light_lampblack_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                }
            },
            Platform.SELECT: {
                "left_cookmode": {
                    "options": {
                        "default": {"left_cookmode": "default"},
                        "order": {"left_cookmode": "order"},
                        "keep_temperature": {"left_cookmode": "keep_temperature"},
                        "local_recipe": {"left_cookmode": "local_recipe"},
                        "cloud_recipe": {"left_cookmode": "cloud_recipe"},
                        "order_keep_temperature": {"left_cookmode": "order_keep_temperature"},
                    }
                },
                "left_gear": {
                    "options": {
                        "0": {"left_gear": 0},
                        "1": {"left_gear": 1},
                        "2": {"left_gear": 2},
                        "3": {"left_gear": 3},
                        "4": {"left_gear": 4},
                        "5": {"left_gear": 5},
                        "6": {"left_gear": 6},
                        "7": {"left_gear": 7},
                        "8": {"left_gear": 8},
                        "9": {"left_gear": 9}
                    }
                },
            },
            Platform.SENSOR: {
                "left_recipe_current_step_action": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "left_recipe_id": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "left_recipe_rest_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_current_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_status": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "eq_recipe_action": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "gas_leakage_code": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "left_work_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_recipe_current_step": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "left_recipe_target_steps": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "left_recipe_target_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_type": {
                    "device_class": SensorDeviceClass.ENUM,
                }
            },
            Platform.BINARY_SENSOR: {
                "is_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
            }
        }
    }
}
