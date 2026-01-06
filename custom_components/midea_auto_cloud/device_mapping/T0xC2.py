from homeassistant.const import Platform
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "calculate": {
            "get": [],
            "set": []
        },
        "entities": {
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "auto_rinse": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "auto_deodorization": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "light_sensor": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "auto_eco": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "sedentary_remind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "clean_mode": {
                    "options": {
                        "无": {"clean_mode": "invalid"},
                        "臀洗": {"clean_mode": "normal"},
                        "妇洗": {"clean_mode": "woman"},
                        "喷杆清洁保养": {"clean_mode": "maintain"},
                    }
                },
                "dry_gear": { # 风温档位调节
                     "options": {
                        "空档": {"dry_gear": 0},
                        "低档": {"dry_gear": 1},
                        "中档": {"dry_gear": 2},
                        "高档": {"dry_gear": 3},
                    }
                },
                "water_gear": { # 水温档位调节
                     "options": {
                        "空档": {"water_gear": 0},
                        "低档": {"water_gear": 1},
                        "中低档": {"water_gear": 2},
                        "中档": {"water_gear": 3},
                        "中高档": {"water_gear": 4},
                        "高档": {"water_gear": 5},
                    }
                },
                "seat_gear": { # 坐圈温度调节
                    "options": {
                        "空档": {"seat_gear": 0},
                        "低档": {"seat_gear": 1},
                        "中低档": {"seat_gear": 2},
                        "中档": {"seat_gear": 3},
                        "中高档": {"seat_gear": 4},
                        "高档": {"seat_gear": 5},
                    }
                },
                "rinse_volume": { # 冲水模式
                    "options": {
                        "大冲": {"rinse_volume": "full"},
                        "小冲": {"rinse_volume": "half"},
                        "无": {"rinse_volume": "invalid"}
                    }
                },
                "injector_position_normal": { # 臀洗喷嘴位置
                    "options": {
                        "空档": {"injector_position_normal": 0},
                        "后档": {"injector_position_normal": 1},
                        "中后档": {"injector_position_normal": 2},
                        "中档": {"injector_position_normal": 3},
                        "中前档": {"injector_position_normal": 4},
                        "前档": {"injector_position_normal": 5},
                    }
                },
                "injector_position_woman": { # 妇洗喷嘴位置
                    "options": {
                        "空档": {"injector_position_woman": 0},
                        "后档": {"injector_position_woman": 1},
                        "中后档": {"injector_position_woman": 2},
                        "中档": {"injector_position_woman": 3},
                        "中前档": {"injector_position_woman": 4},
                        "前档": {"injector_position_woman": 5},
                    }
                },
                "water_pressure_normal": { # 臀洗冲洗强度
                    "options": {
                        "空档": {"water_pressure_normal": 0},
                        "低档": {"water_pressure_normal": 1},
                        "中低档": {"water_pressure_normal": 2},
                        "中档": {"water_pressure_normal": 3},
                        "中高档": {"water_pressure_normal": 4},
                        "高档": {"water_pressure_normal": 5},
                    }
                },
                "water_pressure_woman": {  # 妇洗冲洗强度
                    "options": {
                        "空档": {"water_pressure_woman": 0},
                        "低档": {"water_pressure_woman": 1},
                        "中低档": {"water_pressure_woman": 2},
                        "中档": {"water_pressure_woman": 3},
                        "中高档": {"water_pressure_woman": 4},
                        "高档": {"water_pressure_woman": 5},
                    }
                },
            },
            Platform.SENSOR: {
                "filter_use_per": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
            },
            Platform.BINARY_SENSOR: {
                "on_seat": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
            }
        }
    }
}

