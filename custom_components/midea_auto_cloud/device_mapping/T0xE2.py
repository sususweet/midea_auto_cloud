from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE, PRECISION_HALVES
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "manufacturer": "美的",
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power", "temperature", "mode", "heat", "music", "ti_protect", "fast_wash",
            "ali_manager", "water_quality", "rate", "ele_exception", "communication_error",
            "cur_rate", "sterilize_left_days", "uv_sterilize_minute", "uv_sterilize_second",
            "eplus", "summer", "winter", "efficient", "night", "bath_person", "cloud",
            "bath", "half_heat", "whole_heat", "sterilization", "frequency_hot", "scene",
            "big_water", "wash", "negative_ions", "screen_off", "t_hot", "baby_wash",
            "dad_wash", "mom_wash", "wash_with_temp", "single_wash", "people_wash",
            "wash_temperature", "one_egg", "two_egg", "always_fell", "smart_sterilize",
            "sterilize_cycle_index", "sound_dad", "screen_light", "morning_night_bash",
            "version", "tds_value", "door_status", "limit_error", "sensor_error",
            "scene_id", "auto_off", "clean", "volume", "passwater_lowbyte", "cloud_appoint",
            "protect", "midea_manager", "sleep", "memory", "shower", "scroll_hot",
            "fast_hot_power", "hot_power", "safe", "water_flow", "heat_water_level",
            "flow", "appoint_wash", "now_wash", "end_time_hour", "end_time_minute",
            "get_time", "get_temp", "func_select", "warm_power", "type_select",
            "cur_temperature", "sterilize_high_temp", "discharge_status", "top_temp",
            "bottom_heat", "top_heat", "show_h", "uv_sterilize", "machine", "error_code",
            "need_discharge", "elec_warning", "bottom_temp", "water_cyclic", "water_system",
            "discharge_left_time", "in_temperature", "mg_remain", "waterday_lowbyte",
            "waterday_highbyte", "tech_water", "protect_show", "appoint_power"
        ],
        "entities": {
            Platform.WATER_HEATER: {
                "water_heater": {
                    "power": "power",
                    "operation_list": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "auto": {"power": "on", "mode": "auto"},
                        "eco": {"power": "on", "mode": "eco"},
                        "fast": {"power": "on", "mode": "fast"}
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
                "ti_protect": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "efficient": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "bath": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "half_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "whole_heat": {
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
                "shower": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "fast_hot_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "hot_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "safe": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_flow": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "bottom_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "top_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SELECT: {
                "mode": {
                    "options": {
                        "none": {"mode": "none"},
                        "heat": {"mode": "heat"},
                        "auto": {"mode": "auto"},
                        "eco": {"mode": "eco"},
                        "fast": {"mode": "fast"}
                    }
                },
                "water_quality": {
                    "options": {
                        "0": {"water_quality": 0},
                        "1": {"water_quality": 1},
                        "2": {"water_quality": 2},
                        "3": {"water_quality": 3}
                    }
                },
                "func_select": {
                    "options": {
                        "low": {"func_select": "low"},
                        "medium": {"func_select": "medium"},
                        "high": {"func_select": "high"}
                    }
                },
                "type_select": {
                    "options": {
                        "normal": {"type_select": "normal"},
                        "eco": {"type_select": "eco"},
                        "fast": {"type_select": "fast"}
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

