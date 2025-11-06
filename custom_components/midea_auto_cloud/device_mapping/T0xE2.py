from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "manufacturer": "美的",
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.NUMBER: {
                "water_quality": {
                    "min": 0,
                    "max": 3,
                    "step": 1
                },
                "cur_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "state_class": SensorStateClass.MEASUREMENT,
                }
            },
            Platform.CLIMATE: {
                "water_heater": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on"},
                    },
                    "target_temperature": "temperature",
                    "current_temperature": "cur_temperature",
                    "min_temp": 30,
                    "max_temp": 75,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ti_protect": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "auto_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "protect": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sleep": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "memory": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "safe": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_flow": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SELECT: {
                "func_select": {
                    "options": {
                        "low": {"func_select": "low"},
                        "medium": {"func_select": "medium"}
                    }
                },
                "type_select": {
                    "options": {
                        "normal": {"type_select": "normal"},
                        "valve": {"type_select": "valve"},
                    }
                },
                "machine": {
                    "options": {
                        "real_machine": {"machine": "real_machine"},
                        "virtual_machine": {"machine": "virtual_machine"}
                    }
                }
            },
            Platform.SENSOR: {
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cur_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "top_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "bottom_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "in_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "passwater_lowbyte": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "L",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "passwater_highbyte": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "L",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "rate": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "L/min",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cur_rate": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "L/min",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sterilize_left_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "uv_sterilize_minute": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "uv_sterilize_second": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "screen_light": {
                    "device_class": SensorDeviceClass.ILLUMINANCE,
                    "unit_of_measurement": "lx",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "morning_night_bash": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "tds_value": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "ppm",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "heat_water_level": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "flow": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "L/min",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "end_time_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "end_time_minute": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "wash_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sterilize_cycle_index": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "discharge_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "water_system": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "discharge_left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "mg_remain": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "mg",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "waterday_lowbyte": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "L",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "waterday_highbyte": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "L",
                    "state_class": SensorStateClass.MEASUREMENT
                }
            },
            Platform.BINARY_SENSOR: {
                "door_status": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "limit_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "sensor_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "communication_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "ele_exception": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "elec_warning": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            }
        }
    }
}

