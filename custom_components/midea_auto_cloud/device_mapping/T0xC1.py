from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, UnitOfPower, UnitOfVolumeFlowRate
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[rated_power]",
                    "rvalue": "[rate_high] * 256 + [rate_lower]"
                },
                {
                    "lvalue": "[current_power]",
                    "rvalue": "[cur_rate_high] * 256 + [cur_rate_lower]"
                }
            ],
            "set": []
        },
        "entities": {
            Platform.WATER_HEATER: {
                "water_heater": {
                    "power": "power",
                    "operation_list": {
                        "off": {"power": "off"},
                        "heat": {"power": "on"},
                    },
                    "target_temperature": "bash_target_temperature",
                    "current_temperature": "bash_temperature",
                    "min_temp": 30,
                    "max_temp": 75,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                }
            },
            Platform.CLIMATE: {
                "heating": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "heating_mode": 1},
                    },
                    "target_temperature": "heating_target_temperature",
                    "current_temperature": "heating_temperature",
                    "min_temp": 30,
                    "max_temp": 75,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                }
            },
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "buzzer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "pump": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wait_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "hot_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "warm_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cold_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sleep_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "appoint_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SELECT: {
                "hot_style": {
                    "options": {
                        "1": {"hot_style": 1},
                        "2": {"hot_style": 2},
                    }
                },
                "bash_mode": {
                    "options": {
                        "0": {"bash_mode": 0},
                        "1": {"bash_mode": 1},
                        "2": {"bash_mode": 2},
                        "3": {"bash_mode": 3},
                    }
                },
                "heating_mode": {
                    "options": {
                        "0": {"heating_mode": 0},
                        "1": {"heating_mode": 1},
                        "2": {"heating_mode": 2},
                        "3": {"heating_mode": 3},
                    }
                },
                "three_way_mode": {
                    "options": {
                        "heating": {"three_way_mode": "heating"},
                        "bath": {"three_way_mode": "bath"},
                    }
                },
                "heating_unit_type": {
                    "options": {
                        "floor_heating": {"heating_unit_type": "floor_heating"},
                        "radiator": {"heating_unit_type": "radiator"},
                    }
                },
            },
            Platform.NUMBER: {
                "bash_target_temperature": {
                    "min": 30,
                    "max": 75,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                },
                "bash_gap_temperature": {
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                },
                "heating_target_temperature": {
                    "min": 30,
                    "max": 75,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                },
                "heating_gap_temperature": {
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                },
                "last_time": {
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS,
                },
                "user_mode_target_temperature": {
                    "min": 30,
                    "max": 75,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                },
                "activity_mode_target_temperature": {
                    "min": 30,
                    "max": 75,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                },
                "sleep_mode_target_temperature": {
                    "min": 30,
                    "max": 75,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                },
                "light_gear": {
                    "min": 0,
                    "max": 7,
                    "step": 1,
                },
            },
            Platform.SENSOR: {
                "in_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "out_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "bash_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "bash_target_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "heating_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "heating_target_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "heating_gap_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "user_mode_target_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "activity_mode_target_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sleep_mode_target_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "rated_power": {
                    "device_class": SensorDeviceClass.POWER,
                    "unit_of_measurement": UnitOfPower.WATT,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "current_power": {
                    "device_class": SensorDeviceClass.POWER,
                    "unit_of_measurement": UnitOfPower.WATT,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "flow_volume": {
                    "device_class": SensorDeviceClass.ENUM,
                    "unit_of_measurement": UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "last_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "bash_mode": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "heating_mode": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "hot_style": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "bash_function": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "three_way_mode": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "heating_unit_type": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "light_gear": {
                    "device_class": SensorDeviceClass.ENUM
                },
            },
            Platform.BINARY_SENSOR: {
                "wait_power": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
                "hot_power": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
                "warm_power": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
                "cold_power": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
                "sleep_power": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
                "appoint_power": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
            }
        }
    }
}

