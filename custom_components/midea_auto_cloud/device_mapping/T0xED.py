from homeassistant.const import Platform, UnitOfTemperature,  UnitOfPressure, UnitOfTime, UnitOfElectricPotential, \
    UnitOfVolume, UnitOfMass, PERCENTAGE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": ["custom_temperature_1"],
        "entities": {
            Platform.SELECT: {
                "heat_start": {
                    "options": {
                        "start": {"heat_start": 1},
                        "stop": {"heat_start": 0}
                    },
                }
            },
            Platform.NUMBER: {
                "custom_temperature_1": {
                    "min": 87,
                    "max": 100,
                    "step": 1,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "translation_key": "target_temperature",
                    "command": {
                        "heat_start": 1,
                    }
                },
                "keep_warm_time": {
                    "min": 1,
                    "max": 24,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "command": {
                        "keep_warm": "on",
                    }
                },
            },
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cool": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sleep": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "keep_warm": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "germicidal": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "drainage": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "soften": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "regeneration": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "maintenance_reminder_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "leak_water_protection": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "micro_leak_protection": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cl_sterilization": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.BINARY_SENSOR: {
                "heat_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "lack_water": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "standby_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "chlorine_sterilization_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "rtc_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "low_salt": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "no_salt": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "low_battery": {
                    "device_class": BinarySensorDeviceClass.BATTERY,
                },
                "flowmeter_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "salt_level_sensor_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "leak_water": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "micro_leak": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "maintenance_remind": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            },
            Platform.SENSOR: {
                "current_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "input_temperature_Sensing": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "input_temperature_sensing"
                },
                "hot_pot_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cool_target_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_consumption": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": UnitOfVolume.LITERS,
                    "state_class": SensorStateClass.TOTAL_INCREASING
                },
                "water_consumption_ml": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": UnitOfVolume.MILLILITERS,
                    "state_class": SensorStateClass.TOTAL_INCREASING
                },
                "keep_warm_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "warm_left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "salt_alarm_threshold": {
                    "device_class": SensorDeviceClass.WEIGHT,
                    "unit_of_measurement": UnitOfMass.KILOGRAMS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_salt": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_consumption_today": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": UnitOfVolume.LITERS,
                    "state_class": SensorStateClass.TOTAL_INCREASING
                },
                "water_consumption_average": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": UnitOfVolume.LITERS,
                    "state_class": SensorStateClass.TOTAL_INCREASING
                },
                "regeneration_count": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "use_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.TOTAL_INCREASING
                },
                "flushing_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pre_regeneration_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "remind_maintenance_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "micro_leak_protection_value": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "velocity": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "life_1": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": PERCENTAGE,
                },
                "life_2": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": PERCENTAGE,
                },
                "in_tds": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "mg/L",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "out_tds": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "mg/L",
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    },
    "63000629": {
        "rationale": ["off", "on"],
        "queries": [{"query_type": 6}],
        "centralized": [],
        "entities": {
            Platform.SELECT: {
                "heat_start": {
                    "options": {
                        "start": {"heat_start": 1},
                        "stop": {"heat_start": 0}
                    }
                },
                "custom_temperature_1": {
                    "options": {
                        "45℃": {"custom_temperature_1": 45},
                        "50℃": {"custom_temperature_1": 50},
                        "55℃": {"custom_temperature_1": 55},
                        "80℃": {"custom_temperature_1": 80},
                        "90℃": {"custom_temperature_1": 90},
                        "95℃": {"custom_temperature_1": 95},
                        "100℃": {"custom_temperature_1": 100}
                    },
                    "translation_key": "custom_temperature"
                },
                "keep_warm_time": {
                    "options": {
                        "1h": {"keep_warm_time": 1},
                        "2h": {"keep_warm_time": 2},
                        "3h": {"keep_warm_time": 3},
                        "4h": {"keep_warm_time": 4},
                        "5h": {"keep_warm_time": 5},
                        "6h": {"keep_warm_time": 6},
                        "7h": {"keep_warm_time": 7},
                        "8h": {"keep_warm_time": 8},
                        "9h": {"keep_warm_time": 9},
                        "10h": {"keep_warm_time": 10},
                        "11h": {"keep_warm_time": 11},
                        "12h": {"keep_warm_time": 12},
                        "13h": {"keep_warm_time": 13},
                        "14h": {"keep_warm_time": 14},
                        "15h": {"keep_warm_time": 15},
                        "16h": {"keep_warm_time": 16},
                        "17h": {"keep_warm_time": 17},
                        "18h": {"keep_warm_time": 18},
                        "19h": {"keep_warm_time": 19},
                        "20h": {"keep_warm_time": 20},
                        "21h": {"keep_warm_time": 21},
                        "22h": {"keep_warm_time": 22},
                        "23h": {"keep_warm_time": 23},
                        "24h": {"keep_warm_time": 24}
                    },
                    "command": {
                        "keep_warm": "on",
                    }
                }
            },
            Platform.SWITCH: {
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "child_lock"
                },
                "sleep": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "screen_off"
                },
                "keep_warm": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.BINARY_SENSOR: {
                "heat_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "out_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "out_hot_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "standby_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "lack_water": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            },
            Platform.SENSOR: {
                "current_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_consumption": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": "L",
                    "state_class": SensorStateClass.TOTAL_INCREASING
                },
                "keep_warm_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "ice_gall_status": {
                    "device_class": SensorDeviceClass.ENUM,
                }
            }
        }
    },
    "63200854": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "entities": {
            Platform.SWITCH: {
                "open_close_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "open_close_switch"
                },
                "leak_water_protect": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "leak_water_protection"
                },
                "start_clean": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "start_clean"
                },
            },
            Platform.SELECT: {
                "clean_interval": {
                    "options": {
                        "off": {"clean_interval": "0"},
                        "7天": {"clean_interval": "7"},
                        "15天": {"clean_interval": "15"},
                        "30天": {"clean_interval": "30"}    
                    },
                    "translation_key": "clean_interval"
                }
            },
            Platform.NUMBER: {
                "clean_water_consumption": {
                    "min": 0,
                    "max": 60,
                    "step": 1,
                    "translation_key": "clean_water_consumption"
                },
            },
            Platform.SENSOR: {
                "input_temperature_Sensing": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "input_temperature_sensing"
                },
                "input_pressure_Sensing": {
                    "device_class": SensorDeviceClass.PRESSURE,
                    "unit_of_measurement": "MPa",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "water_gage"
                },
                "all_water_consumption": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "m³",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "water_consumption_big"
                },
                "water_flow": {
                    "device_class": SensorDeviceClass.VOLUME_FLOW_RATE,
                    "unit_of_measurement": "L/min",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "water_flow"
                },
                "clean_water_consumption_next_remaining": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "clean_water_consumption_next_remaining"
                },
                "clean_interval_next_days_remaining": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": "d",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "clean_interval_next_days_remaining"
                },
            },
        } 
    },
    "632009EN": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "entities": {
            Platform.SWITCH: {
                "heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "Heat_function"
                },
                "antifreeze": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "antifreeze"
                },
                "wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "filter_element_flushing"
                },
                "no_obsolete_water": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "no_obsolete_water"
                },
                "save_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "save_mode"
                }
            },
            Platform.NUMBER: {
                "quantify_21": {
                    "min": 300,
                    "max": 500,
                    "step": 100,
                    "translation_key": "quantify_21",
                    "unit_of_measurement": "mL"
                },
                "quantify_22": {
                    "min": 500,
                    "max": 1000,
                    "step": 100,
                    "translation_key": "quantify_22",
                    "unit_of_measurement": "mL"
                },
                "quantify_23": {
                    "min": 1000,
                    "max": 1500,
                    "step": 100,
                    "translation_key": "quantify_23",
                    "unit_of_measurement": "mL"
                }
            },
            Platform.SENSOR: {
                "in_tds": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "mg/L",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "in_tds"
                },
                "out_tds": {
                    "device_class": SensorDeviceClass.WATER,
                    "unit_of_measurement": "mg/L",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "out_tds"
                },
                "life_1": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "life_1"
                },
                "life_2": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "life_2_PCB"
                },
                "water_consumption": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": "mL",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "water_consumption"
                },
                "hot_pot_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": "°C",
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "hot_pot_temperature"
                },
                "heat_start": {
                    "name": "1=加热中/2=保温中",
                    "device_class": SensorDeviceClass.ENUM
                }
            },
            Platform.BINARY_SENSOR: {
                "out_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "translation_key": "out_water"
                },
                "out_hot_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "translation_key": "out_hot_water"
                }
            }
        } 

    }
}
