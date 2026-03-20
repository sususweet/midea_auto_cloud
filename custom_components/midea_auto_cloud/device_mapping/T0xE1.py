from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": [0, 1],
        "queries": [{}],
        # 注意：lua 协议中烘干存储（dryswitch）的时长字段是 dry_set_min
        # air_set_hour 在此设备上更偏向“烘干/风量相关”的另一路时间字段。
        # 因此 centralized 要携带 dry_set_min，避免 HA 开启/关闭烘干存储时下发 dry_set_min=0xff 导致异常/清零。
        "centralized": ["dry_set_min"],
        "entities": {
            Platform.SWITCH: {
                "airswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dryswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dry_step_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    # lua 解析时：bit=1 -> dry_step_switch=0，bit=0 -> dry_step_switch=1（反逻辑）
                    # 所以这里反置 rationale，保证 HA 展示与真实开关一致，且控制方向也正确。
                    "rationale": [1, 0],
                }
            },
            Platform.NUMBER: {
                "air_set_hour": {
                    "min": 1,
                    "max": 72,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    # 兼容原有 HA 实体 key 与翻译：界面上仍显示“烘干存储设置时间”
                    # 实际控制/读取 dry_set_min（lua 使用字段名）
                    "attribute": "dry_set_min",
                }
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "air_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "water_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "wash_stage":{
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "diy_flag": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_main_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_piao_wash": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "diy_times": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
            },
            Platform.SELECT: {
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off" },
                        "power_on": {"work_status": "power_on" },
                        "cancel": {"work_status": "cancel" },
                        "pause": {"operator":"pause"},
                        "resume": {"operator":"start"},
                    }
                },
                "wash_mode": {
                    "options": {
                        "neutral_gear": {"work_status": "work", "mode": "neutral_gear"},
                        "auto_wash": {"work_status": "work", "mode": "auto_wash"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "eco_wash": {"work_status":"work","mode":"eco_wash","additional":0,"wash_region":3},
                        "glass_wash": {"work_status": "work", "mode": "glass_wash"},
                        "hour_wash": {"work_status": "work", "mode": "hour_wash"},
                        "fast_wash": {"work_status": "work", "mode": "fast_wash"},
                        "soak_wash": {"work_status": "work", "mode": "soak_wash"},
                        "90min_wash": {"work_status": "work", "mode": "90min_wash"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit_wash"},
                        "self_define": {"work_status": "work", "mode": "self_define"},
                        "germ": {"work_status": "work", "mode": "germ"},
                        "bowl_wash": {"work_status": "work", "mode": "bowl_wash"},
                        "kill_germ": {"work_status": "work", "mode": "kill_germ"},
                        "seafood_wash": {"work_status": "work", "mode": "seafood_wash"},
                        "hotpot_wash": {"work_status": "work", "mode": "hotpot_wash"},
                        "quietnight_wash": {"work_status": "work", "mode": "quietnight_wash"},
                        "less_wash": {"work_status": "work", "mode": "less_wash"},
                        "oilnet_wash": {"work_status": "work", "mode": "oilnet_wash"}
                    }
                }
            },
            Platform.SENSOR: {
                "bright": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "softwater": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    },
   "7600V1E7": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": ["air_set_hour"],
        "entities": {
            Platform.SWITCH: {
                "airswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "child_lock"
                }
            },
            Platform.NUMBER: {
                "air_set_hour": {
                    "min": 1,
                    "max": 72,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS
                }
            },
            Platform.SELECT: {
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off" },
                        "power_on": {"work_status": "power_on" },
                        "cancel": {"work_status": "cancel" },
                        "pause": {"operator":"pause"},
                        "resume": {"operator":"start"},
                    }
                },
                "wash_mode": {
                    "options": {
                        "neutral_gear": {"work_status": "work", "mode": "neutral_gear"},
                        "auto_wash": {"work_status": "work", "mode": "auto_wash"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "eco_wash": {"work_status":"work","mode":"eco_wash","additional":0,"wash_region":3},
                        "soft_wash": {"work_status": "work", "mode": "glass_wash"},
                        "fast_wash": {"work_status": "work", "mode": "fast_wash"},
                        "soak_wash": {"work_status": "work", "mode": "soak_wash"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit_wash"}
                    }
                }
            },
            Platform.SENSOR: {
                "bright": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
