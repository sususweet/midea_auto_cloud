from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power_state", "run_mode", "temp_set", "heat_enable", "cool_enable"
        ],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power_state",
                    "hvac_modes": {
                        "off": {"power_state": "off"},
                        "heat": {"power_state": "on", "run_mode": "heat", "heat_enable": "on"},
                        "cool": {"power_state": "on", "run_mode": "cool", "cool_enable": "on"},
                        "auto": {"power_state": "on", "run_mode": "auto", "heat_enable": "on", "cool_enable": "on"}
                    },
                    "target_temperature": "temp_set",
                    "current_temperature": "cur_temp",
                    "pre_mode": "mode",
                    "min_temp": 5,
                    "max_temp": 70,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "freeze_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "power_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "heat_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cool_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "silence_set_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "time_set_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "silence_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "holiday_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "holiday_set_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "holiday_on_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "room_temp_ctrl": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "room_temp_set": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "comp_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "day_time_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "week_time_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "warn_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "defrost_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "pre_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "run_mode": {
                    "options": {
                        "heat": {"run_mode": "heat"},
                        "cool": {"run_mode": "cool"},
                        "auto": {"run_mode": "auto"},
                        "fan": {"run_mode": "fan"},
                        "dry": {"run_mode": "dry"}
                    }
                },
                "temp_type": {
                    "options": {
                        "water_temperature": {"temp_type": "water_temperature"},
                        "room_temperature": {"temp_type": "room_temperature"},
                        "outdoor_temperature": {"temp_type": "outdoor_temperature"}
                    }
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "cur_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "heat_max_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "heat_min_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cool_max_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cool_min_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "auto_max_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "auto_min_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "preheat_on_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "preheat_max_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "preheat_min_set_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temp_set": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
