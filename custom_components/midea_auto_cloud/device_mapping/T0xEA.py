from homeassistant.const import Platform, UnitOfElectricPotential, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": [0, 1],
        "queries": [{}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[remaining_time]",
                    "rvalue": "[left_time_hour] * 60 + [left_time_min]"
                },
                {
                    "lvalue": "[warming_time]",
                    "rvalue": "[warm_time_hour] * 60 + [warm_time_min]"
                },
                {
                    "lvalue": "[delay_time]",
                    "rvalue": "[order_time_hour] * 60 + [order_time_min]",
                }
            ],
            "set": {
            }
        },
        "entities": {
            Platform.SENSOR: {
                "work_stage": {},
                "voltage": {
                    "device_class": SensorDeviceClass.VOLTAGE,
                    "unit_of_measurement": UnitOfElectricPotential.VOLT,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "top_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "bottom_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "remaining_time": {
                    "unit_of_measurement": UnitOfTime.MINUTES
                },
                "warming_time": {
                    "unit_of_measurement": UnitOfTime.MINUTES
                },
                "delay_time": {
                    "unit_of_measurement": UnitOfTime.MINUTES
                },
            },
            Platform.BINARY_SENSOR: {
                "top_hot": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
                "flank_hot": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
                "bottom_hot": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                }
            },
            Platform.SELECT: {
                "mode": {
                    "options": {
                        "精华饭": {"mode": "essence_rice", "work_status": "cooking"},
                        "稀饭": {"mode": "gruel", "work_status": "cooking"},
                        "热饭": {"mode": "heat_rice", "work_status": "cooking"},
                        "煮粥": {"mode": "boil_congee", "work_status": "cooking"},
                        "煲汤": {"mode": "cook_soup", "work_status": "cooking"},
                        "蒸煮": {"mode": "stewing", "work_status": "cooking"},
                    }
                },
                "rice_type": {
                    "options": {
                        "无": {"rice_type": "none"},
                        "东北大米": {"rice_type": "northeast"},
                        "长粒米": {"rice_type": "longrain"},
                        "香米": {"rice_type": "fragrant"},
                        "五常大米": {"rice_type": "five"},
                    }
                },
                "work_status": {
                    "options": {
                        "停止": {"work_status": "cancel"},
                        "烹饪": {"work_status": "cooking"},
                        "保温": {"work_status": "keep_warm"},
                        "醒米": {"work_status": "awakening_rice"},
                        "预约": {"work_status": "schedule"}
                    }
                }
            }
        }
    },
    "61001527": {
        "rationale": [0, 1],
        "queries": [{}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[remaining_time]",
                    "rvalue": "[left_time_hour] * 60 + [left_time_min]"
                },
                {
                    "lvalue": "[warming_time]",
                    "rvalue": "[warm_time_hour] * 60 + [warm_time_min]"
                },
                {
                    "lvalue": "[delay_time]",
                    "rvalue": "[order_time_hour] * 60 + [order_time_min]",
                }
            ],
            "set": {
            }
        },
        "entities": {
            Platform.SENSOR: {
                "work_stage": {},
                "voltage": {
                    "device_class": SensorDeviceClass.VOLTAGE,
                    "unit_of_measurement": UnitOfElectricPotential.VOLT,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "top_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "bottom_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "remaining_time": {
                    "unit_of_measurement": UnitOfTime.MINUTES
                },
                "warming_time": {
                    "unit_of_measurement": UnitOfTime.MINUTES
                },
                "delay_time": {
                    "unit_of_measurement": UnitOfTime.MINUTES
                },
            },
            Platform.SELECT: {
                "mode": {
                    "options": {
                        "精华饭": {"mode": "essence_rice", "work_status": "cooking"},
                        "稀饭": {"mode": "gruel", "work_status": "cooking"},
                        "热饭": {"mode": "heat_rice", "work_status": "cooking"},
                        "煮粥": {"mode": "boil_congee", "work_status": "cooking"},
                        "煲汤": {"mode": "cook_soup", "work_status": "cooking"},
                        "蒸煮": {"mode": "stewing", "work_status": "cooking"},
                    }
                },
                "rice_type": {
                    "options": {
                        "无": {"rice_type": "none"},
                        "东北大米": {"rice_type": "northeast"},
                        "长粒米": {"rice_type": "longrain"},
                        "香米": {"rice_type": "fragrant"},
                        "五常大米": {"rice_type": "five"},
                    }
                },
                "work_status": {
                    "options": {
                        "停止": {"work_status": "cancel"},
                        "烹饪": {"work_status": "cooking"},
                        "保温": {"work_status": "keep_warm"},
                        "醒米": {"work_status": "awakening_rice"},
                        "预约": {"work_status": "schedule"},
                    }
                }
            }
        }
    }
}
