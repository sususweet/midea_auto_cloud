from homeassistant.const import Platform, UnitOfElectricPotential, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{"query_type": "db"}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[remaining_time]",
                    "rvalue": "[db_remain_time]"
                }
            ],
            "set": {
            }
        },
        "entities": {
            Platform.BINARY_SENSOR: {
                "db_door_opened": {
                    "device_class": BinarySensorDeviceClass.OPENING,
                    "translation_key": "door_opened"
                },
                "db_bucket_water_overheating": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                    "translation_key": "bucket_water_overheating"
                },
                "db_drying_tunnel_overheating": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                    "translation_key": "drying_tunnel_overheating"
                },
                "db_detergent_needed": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                    "translation_key": "detergent_lack"
                }
            },
            Platform.LOCK: {
                "db_baby_lock": {
                    "rationale": [0, 1],
                    "translation_key": "child_lock",
                },
            },
            Platform.SWITCH: {
                "db_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "db_control_status": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["pause", "start"],
                    "translation_key": "control_status",
                },
            },
            Platform.SELECT: {
                "db_location_selection": {
                    "options": {
                        "left": {"db_location_selection": "left"},
                        "right": {"db_location_selection": "right"}
                    }
                },
                "db_program": {
                    "options": {
                        "baby_clothes": {"db_program": "baby_clothes"},
                        "baby_clothes_dry": {"db_program": 151},
                        "clean_stains": {"db_program": "clean_stains"},
                        "cold_wash": {"db_program": "cold_wash"},
                        "cook_wash": {"db_program": "cook_wash"},
                        "fast_wash": {"db_program": 137},
                        "hot_wind_dry": {"db_program": 153},
                        "rinsing_dehydration": {"db_program": "rinsing_dehydration"},
                        "self_wash_5": {"db_program": "self_wash_5"},
                        "single_dehytration": {"db_program": "single_dehytration"},
                        "single_drying": {"db_program": "single_drying"},
                        "small_wash_dry": {"db_program": 138},
                        "socks": {"db_program": 148},
                        "standard": {"db_program": "standard"},
                        "underpants": {"db_program": 156},
                        "underwear": {"db_program": "underwear"},
                        "water_ssp": {"db_program": "water_ssp"}
                   }
                },
                "db_temperature": {
                    "options": {
                        "冷水": {"db_temperature": 0},
                        "30℃": {"db_temperature": 3},
                        "40℃": {"db_temperature": 4},
                        "60℃": {"db_temperature": 5},
                        "95℃": {"db_temperature": 6}
                    },
                    "translation_key": "temperature"
                },
                "db_detergent": {
                    "options": {
                        "关闭": {"db_detergent": 0},
                        "L1": {"db_detergent": 1},
                        "L2": {"db_detergent": 2},
                        "L3": {"db_detergent": 3}
                    },
                    "translation_key": "detergent"
                },
                "db_dehydration_speed": {
                    "options": {
                        "免脱水": {"db_dehydration_speed": 0},
                        "800转": {"db_dehydration_speed": 3},
                        "1000转": {"db_dehydration_speed": 4}
                    },
                    "translation_key": "dehydration_speed"
                },
                "db_rinse_count": {
                    "options": {
                        "1次": {"db_rinse_count": 1},
                        "2次": {"db_rinse_count": 2},
                        "3次": {"db_rinse_count": 3},
                        "4次": {"db_rinse_count": 4},
                        "5次": {"db_rinse_count": 5}
                    },
                    "translation_key": "soak_count"
                },
                "db_dry": {
                    "options": {
                        "关闭": {"db_dry": 0},
                        "智能": {"db_dry": 1},
                        "定时240": {"db_dry": 12},
                        "定时180": {"db_dry": 11},
                        "定时120": {"db_dry": 7},
                        "定时60": {"db_dry": 5},
                        "定时30": {"db_dry": 4}              
                    }
                }
            },
            Platform.SENSOR: {
                "db_remain_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_progress": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "db_running_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "running_status"
                },
                "db_error_code": {
                    "device_class": SensorDeviceClass.ENUM
                }
            }
        }
    }
}


# sn8 38206322（COLMO CLGHZ20DL 复式洗烘机，subtype 12856）：
# 上筒是独立烘干机（lua bucket dc，location 1），下筒是洗衣机（bucket db，location 2）。
# 1) default 只查 db，烘干机状态读不到 → 追加 dc 查询（lua: query_type=dc + dc_location=1 → upDCQueryTable）。
# 2) 程序表按该型号官方配置 midea_json_new/D9/0000.d9.12856.json 下筒 paramData+cycleShop 共 26 个；
#    lua 只接受字符串程序名（default 里 137/138/148… 等数字值会让 lua checkSum 报 nil）。
#    default 里的 underwear(0x0D)/standard 等机器会接收但不加载（剩余时间停在 1），本机内衣是 water_underwear(0x22)。
_D9_38206322_PROGRAMS = [
    # 面板程序
    "water_intelligent", "big", "silk", "water_shirt", "green_wool", "down_jacket",
    "steam_sterilize_wash", "fast_wash_30", "single_dehytration", "ssp",
    # 云程序
    "water_mixed_wash", "fast_wash", "water_eco", "rinsing_dehydration", "water_steep",
    "new_water_cotton", "water_baby_clothes", "water_underwear", "sport_clothes",
    "remove_mite_wash", "color", "spring_autumn_wash", "summer_wash", "winter_wash",
    "bath_towel", "new_clothes_wash",
]

DEVICE_MAPPING["38206322"] = {
    **DEVICE_MAPPING["default"],
    "queries": [{"query_type": "db"}, {"query_type": "dc", "dc_location": 1}],
    "entities": {
        **DEVICE_MAPPING["default"]["entities"],
        Platform.SELECT: {
            **DEVICE_MAPPING["default"]["entities"][Platform.SELECT],
            "db_program": {
                "options": {p: {"db_program": p} for p in _D9_38206322_PROGRAMS}
            },
        },
        Platform.SENSOR: {
            **DEVICE_MAPPING["default"]["entities"][Platform.SENSOR],
            "dc_running_status": {
                "device_class": SensorDeviceClass.ENUM,
                "translation_key": "dc_running_status"
            },
            "dc_remain_time": {
                "device_class": SensorDeviceClass.DURATION,
                "unit_of_measurement": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT
            },
            "dc_program": {
                "device_class": SensorDeviceClass.ENUM
            },
            "dc_dry_status": {
                "device_class": SensorDeviceClass.ENUM
            },
        },
        Platform.NUMBER: {
            # 预约：App 的 onReserve 发 {wash:1, appointment:"on", appointment_time:N}，
            # N = 距「洗完」的分钟数（须大于当前程序剩余时间、≤1440）。
            "db_appointment_time": {
                "min": 0,
                "max": 1440,
                "step": 1,
                "unit_of_measurement": UnitOfTime.MINUTES,
                "command": {
                    "db_control_status": "start",
                    "db_appointment": 1,
                    "db_appointment_time": "{value}"
                },
                "translation_key": "appointment_finish_in"
            },
        },
        Platform.BUTTON: {
            # 取消预约：App 的 cancelReserve 发 {wash:0, appointment:"off", appointment_time:0}
            "cancel_appointment": {
                "command": {
                    "db_control_status": "pause",
                    "db_appointment": 0,
                    "db_appointment_time": 0
                }
            },
        },
    },
}
