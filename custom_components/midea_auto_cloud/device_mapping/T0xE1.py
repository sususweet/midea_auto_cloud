"""T0xE1 dishwasher device mapping and E1-specific logic.

All E1 operational logic (status computation, validators, condition matching,
command building, cloud config merging) lives here.
"""
import json as _json
import datetime as _dt
import logging
from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

_WORK_STATUS_NUM: dict[str, int] = {
    "power_off": 0, "power_on": 1, "cancel": 1, "standby": 1,
    "cancel_order": 1, "order": 2, "work": 3, "error": 4,
    "keep": 5, "dry": 6, "pipeInspect": 10,
}

_STATUS_TEXT: dict[int, str] = {
    -3: "初始化", -2: "保管中", -1: "已离线", 0: "已关机",
    1: "待机中", 2: "预约中", 3: "运行中", 4: "故障", 5: "保管中", 6: "烘干中", 10: "待机中",
}

_LOGGER = logging.getLogger(__name__)

# Cloud-feature → (platform, entity_key) mapping used by apply_device_config
_FEATURE_MAP: dict[str, tuple[str, str]] = {
    "additional":       ("select", "additional"),
    "waterLevel":       ("select", "water_level"),
    "waterStrongLevel": ("select", "water_strong_level"),
    "region":           ("select", "wash_region"),
    "germ":             ("select", "work_time"),
    "autoOpen":         ("switch", "door_auto_open"),
    "autoThrow":        ("switch", "auto_throw"),
    "moreDry":          ("switch", "more_dry"),
    "moreDryWash":      ("switch", "more_dry_wash"),
}

# Select entities rebuilt dynamically from cloud config
_DYNAMIC_SELECTS: dict[str, tuple[str, str]] = {
    "additional":       ("additional",        "additional"),
    "water_level":      ("waterLevel",        "water_level"),
    "water_strong_level":("waterStrongLevel", "water_strong_level"),
    "wash_region":      ("region",            "wash_region"),
}

# Built-in diff fallback (local hardcoded, matching mini-program utils/diff.js).
# Used when cloud diff download fails, ensuring basic diff functionality.
_DEFAULT_DIFF: dict = {
    "diffType": {
        "withoutLockOnStart": ["000W5601","760RX10P","760Y0002","760Y0004","7600JV20","7600061Y","7600062Q","7600646H","7600643T","76000613","76000624","76006440","76006441","76000628","7600644L","76006452","76006456","76006457","76006458","76006455","76006450","7600645A","76006451","7600645B","76006459","7600644Z","7600645J","7600645L","760Y0009","7600645Q","7600059A","7600645D","7600645N","7600645F","760Y0010","76006469","7600646A","76006460","76006467","7600646G","7600646T","7600646L","7600646N","7600646W","7600646Q"],
        "keepOffOnPowerOff": ["000000X4","000000Y1","00000X4S","0000V1E6"],
        "deviceUploadFaltDataOnPower": ["000000K2","000000K1","7600062E"],
        "doorOff": ["00003906"],
        "devOffKeep": ["0000D25A","0000D26A","0000D26W","000000E6","000000E8","000000H1","000000H3","00000H3P","000000H4","000000H5","0HW2601C","000000K1","000000K2","000000L2","000000L3","000000M6","00000P30","000000Q1","0000RX30","000000V1","0000V1E6","00W2601C","00W3602H","00W3602K","00W3802H","00W3909R","000W8501","00W9601B","000000X3","000000X4","00000X4S","000000X5","000000X6","000000Y1","760BLV66","760BLV88","760JD103","760P0P23","760P40T1","760SN101","760TM101","760V1E10","760WE203","7600JV13","7600P30S","7600P40P","7600RX50","7600645H","7600V1E7","7600V1E9","76000D25","76000P40","760000E1","7600061B","7600061C","7600061D","7600061F","7600061H","7600061J","7600061K","7600062B","7600062L","7600643V","76000002","76000009","76000572","76000610","76000614","7600062C","76000623","000000E6","000000E8","00W9601B","760B108B"],
        "withoutOrder": ["00W2601C"],
        "minuteOrder": ["000000MT","760P30PL","7600V1E0","76000CF4","760000GZ","760000V5","7600061E","7600062R"],
        "turnOffOnKeepStart": ["7600644N","76000014","760DB412","760B108B","00000D18","0000D25A","0000D26A","0000D26W","000000E6","000000E8","000000F1","00000F2A","00000F3B","000000F4","000000H1","000000H3","00000H3D","00000H3P","00000H3S","000000H5","0HW2601C","000000J1","000000K1","000000K2","000000L1","000000L2","000000L3","000000M6","000000M7","00000M10","000000MT","00000P10","00000P30","000000Q1","0000RX10","0000RX30","000000S2","000000S3","000000V1","0000V1E6","00W2601C","00W3602H","00W3602K","00W3802H","0W3905CN","00W3909R","000W5601","00W7635R","000W8501","00W9601B","000000X3","000000X4","00000X4S","000000X5","000000X6","000000Y1","760BLV66","760BLV88","760BVL68","760GX6HP","760GX600","760JD103","760JD201","760M10CD","760P0P23","760P0P36","760P40T1","760RX20G","760RX20S","760SN101","760TM101","760V1E10","760WE203","00003906","7600BF01","7600BF03","7600JV13","7600M10P","7600P23Q","7600P30S","7600P40P","7600RX20","7600RX50","7600645H","7600V1E0","7600V1E7","7600V1E9","11111M10","76000CF4","76000D25","76000JV8","76000MG1","76000NS8","76000P40","760000C1","760000E1","760000LX","760000M1","760000M8","760000Q7","760000V2","760000V3","7600061B","7600061C","7600061D","7600061F","7600061H","7600061J","7600061K","7600061Z","7600062B","7600062E","7600062G","7600062L","7600643V","7603602D","7603905P","76000002","76000007","76000009","76000012","76000018","76000572","76000596","76000601","7600646B","76000610","76000614","76000619","76000623"],
        "autoThrowWithMode": ["7600062S"],
        "keepWithoutDry": ["00000P30","000000L3","760WE203","760P0P23","7600JV13","7600P30S","7600RX50","760P30PL","00003906","76000610","7600061F","7600644N","7600061C","7600061D"],
        "additionalSync": ["76000015","76000017","76000628","7600H0P9"],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# DEVICE MAPPING
# ══════════════════════════════════════════════════════════════════════════════
#
#  Key lookup order: subtype → sn8 → default_category → "default"
#  MeijuCloud E1 devices use "auto_default" (full superset), then cloud config
#  filters it via apply_device_config().  MSmartHome devices use the original
#  per-SN8 / "default" entries so behaviour is unchanged from before the restructure.

DEVICE_MAPPING = {
    "default": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
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
                "wash_stage": {
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
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
                "dryswitch": {
                    "options": {
                        "cancel": {"dryswitch": 0},
                        "waiting": {"dryswitch": 1},
                        "running": {"dryswitch": 2},
                    }
                },
                "dry_step_switch": {
                    "options": {
                        "cancel": {"dry_step_switch": 0},
                        "waiting": {"dry_step_switch": 1},
                        "running": {"dry_step_switch": 2},
                    }
                },
                "air_set_hour": {
                    "options": {
                        "12": {"air_set_hour": "12"},
                        "24": {"air_set_hour": "24"},
                        "36": {"air_set_hour": "36"},
                        "48": {"air_set_hour": "48"},
                        "60": {"air_set_hour": "60"},
                        "72": {"air_set_hour": "72"},
                    }
                },
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off"},
                        "power_on": {"work_status": "power_on"},
                        "cancel": {"work_status": "cancel"},
                        "pause": {"operator": "pause"},
                        "resume": {"operator": "start"},
                    }
                },
                "wash_mode": {
                    "options": {
                        "neutral_gear": {"work_status": "work", "mode": "neutral_gear"},
                        "auto_wash": {"work_status": "work", "mode": "auto_wash"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "eco_wash": {"work_status": "work", "mode": "eco_wash", "additional": 0, "wash_region": 3},
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
    "76006481": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
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
                "wash_stage": {
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
            Platform.NUMBER: {
                "air_set_hour": {
                    "min": 1,
                    "max": 72,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS
                }
            },
            Platform.SELECT: {
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
                "dryswitch": {
                    "options": {
                        "cancel": {"dryswitch": 0},
                        "waiting": {"dryswitch": 1},
                        "running": {"dryswitch": 2},
                    }
                },
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off"},
                        "power_on": {"work_status": "power_on"},
                        "cancel": {"work_status": "cancel"},
                        "pause": {"operator": "pause"},
                        "resume": {"operator": "start"},
                    }
                },
                "wash_mode": {
                    "options": {
                        "neutral_gear": {"work_status": "work", "mode": "neutral_gear"},
                        "auto_wash": {"work_status": "work", "mode": "auto_wash"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "eco_wash": {"work_status": "work", "mode": "eco_wash", "additional": 0, "wash_region": 3},
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
    "7600649Q": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "waterswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uvswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
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
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
                "dryswitch": {
                    "options": {
                        "cancel": {"dryswitch": 0},
                        "waiting": {"dryswitch": 1},
                        "running": {"dryswitch": 2},
                    }
                },
                "dry_step_switch": {
                    "options": {
                        "cancel": {"dry_step_switch": 0},
                        "waiting": {"dry_step_switch": 1},
                        "running": {"dry_step_switch": 2},
                    }
                },
                "air_set_hour": {
                     "options": {
                        "12": {"air_set_hour": "12" },
                        "24": {"air_set_hour": "24" },
                        "36": {"air_set_hour": "36" },
                        "48": {"air_set_hour": "48" },
                        "60": {"air_set_hour": "60" },
                        "72": {"air_set_hour": "72" },
                    }
                },
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
        "centralized": [],
        "entities": {
            Platform.LOCK: {
                "lock": {
                    "translation_key": "child_lock",
                },
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
                "airswitch": {
                    "options": {
                        "cancel": {"airswitch": 0},
                        "waiting": {"airswitch": 1},
                        "running": {"airswitch": 2}
                    }
                },
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
    },
    "760Y0026": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": ["additional"],
        "entities": {
            Platform.LOCK: {
                "lock": {
                    "translation_key": "child_lock",
                },
            },
            Platform.SWITCH: {
                "airswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.PROBLEM
                },
                "air_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                }
            },
            Platform.NUMBER: {
                "air_set_hour": {
                    "min": 0,
                    "max": 72,
                    "step": 1,
                    "unit_of_measurement": UnitOfTime.HOURS
                }
            },
            Platform.SELECT: {
                "work_status": {
                    "options": {
                        "power_off": {"work_status": "power_off"},
                        "power_on": {"work_status": "power_on"},
                        "cancel": {"work_status": "cancel"},
                        "pause": {"operator": "pause"},
                        "resume": {"operator": "start"}
                    }
                },
                "wash_mode": {
                    "options": {
                        "neutral_gear": {"work_status": "cancel", "mode": "neutral_gear"},
                        "strong_wash": {"work_status": "work", "mode": "strong_wash"},
                        "standard_wash": {"work_status": "work", "mode": "standard_wash"},
                        "single_disinfect": {"work_status": "work", "mode": "single_disinfect"},
                        "eco_wash": {"work_status": "work", "mode": "eco_wash"},
                        "glass_wash": {"work_status": "work", "mode": "glass_wash"},
                        "fast_wash": {"work_status": "work", "mode": "fast_wash"},
                        "soak_wash": {"work_status": "work", "mode": "soak_wash"},
                        "self_clean": {"work_status": "work", "mode": "self_clean"},
                        "fruit_wash": {"work_status": "work", "mode": "fruit_wash"},
                        "germ": {"work_status": "work", "mode": "germ"},
                        "seafood_wash": {"work_status": "work", "mode": "seafood_wash"},
                        "hotpot_wash": {"work_status": "work", "mode": "hotpot_wash"}
                    }
                },
                "softwater": {
                    "options": {
                        "1": {"softwater": 1},
                        "2": {"softwater": 2},
                        "3": {"softwater": 3},
                        "4": {"softwater": 4},
                        "5": {"softwater": 5},
                        "6": {"softwater": 6}
                    }
                },
                "rinse_aid": {
                    "options": {
                        "1": {"bright": 1},
                        "2": {"bright": 2},
                        "3": {"bright": 3},
                        "4": {"bright": 4},
                        "5": {"bright": 5}
                    }
                },
                "additional": {
                    "options": {
                        "none": {"additional": 0},
                        "extra_rinse_1": {"additional": 9},
                        "extra_rinse_2": {"additional": 10},
                        "few_dishes_extra_rinse_1": {"additional": 13},
                        "few_dishes_extra_rinse_2": {"additional": 14}
                    }
                }
            },
            Platform.SENSOR: {
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "cur_temperature"
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "remain_time"
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "wash_stage": {
                    "device_class": SensorDeviceClass.ENUM
                }
            },
        },
    },
    # ── auto_default: full superset used by MeijuCloud path.
    #     Cloud config (apply_device_config) filters it down per-device.
    "auto_default": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.LOCK: {
                "lock": {"translation_key": "child_lock"},
            },
            Platform.SWITCH: {
                "power": {"validator": ["can_operate:power"]},
                "door_auto_open": {"rationale": [0, 1], "mode_dependent": True, "local_only": True},
                "auto_throw": {"rationale": [0, 1], "mode_dependent": True, "local_only": True},
                "more_dry": {"rationale": [0, 1], "mode_dependent": True, "local_only": True},
                "more_dry_wash": {"rationale": [0, 1], "mode_dependent": True, "local_only": True},
            },
            Platform.BUTTON: {
                "start_wash": {
                    "command_builder": "start_wash",
                    "translation_key": "start",
                    "validator": ["can_operate:start"],
                },
                "start_keep": {
                    "command": {"airswitch": 2},
                    "translation_key": "start_keep",
                    "validator": ["keep", "keep_on", "can_operate:start"],
                },
                "start_dry": {
                    "command": {"dryswitch": 2},
                    "translation_key": "start_dry",
                    "validator": ["dry", "can_operate:start"],
                },
                "cancel": {
                    "command_builder": "cancel",
                    "translation_key": "cancel",
                    "validator": ["can_operate:cancel"],
                },
                "pause": {
                    "command_builder": "pause",
                    "translation_key": "pause",
                    "validator": ["can_operate:pause"],
                },
                "start_order": {
                    "command_builder": "order",
                    "translation_key": "start_order",
                    "validator": ["can_operate:order"],
                },
            },
            Platform.BINARY_SENSOR: {
                "doorswitch": {"device_class": BinarySensorDeviceClass.OPENING, "rationale": [1, 0], "translation_key": "door_opened"},
                "air_status": {"device_class": BinarySensorDeviceClass.RUNNING},
                "water_lack": {"device_class": BinarySensorDeviceClass.PROBLEM, "translation_key": "lack_water"},
                "softwater_lack": {"device_class": BinarySensorDeviceClass.PROBLEM},
                "bright_lack": {"device_class": BinarySensorDeviceClass.PROBLEM},
            },
            Platform.NUMBER: {
                "air_set_hour": {"min": 0, "max": 72, "step": 1, "unit_of_measurement": UnitOfTime.HOURS, "side_effect": {"type": "keep_auto_enable"}},
                "dry_set_min": {"min": 0, "max": 180, "step": 10, "unit_of_measurement": UnitOfTime.MINUTES, "side_effect": {"type": "dry_auto_enable"}},
            },
            Platform.TIME: {
                "order_set_time": {
                    "target_keys": {"hour": "order_target_hour", "minute": "order_target_min"},
                    "time_mode": "direct",
                    "local_only": True,
                },
            },
            Platform.SELECT: {
                "wash_mode": {"options": {"standard_wash": {"mode": "standard_wash"}, "auto_wash": {"mode": "auto_wash"}, "strong_wash": {"mode": "strong_wash"}, "eco_wash": {"mode": "eco_wash", "additional": 0, "wash_region": 3}, "glass_wash": {"mode": "glass_wash"}, "hour_wash": {"mode": "hour_wash"}, "fast_wash": {"mode": "fast_wash"}, "soak_wash": {"mode": "soak_wash"}, "90min_wash": {"mode": "90min_wash"}, "self_clean": {"mode": "self_clean"}, "fruit_wash": {"mode": "fruit_wash"}, "self_define": {"mode": "self_define"}, "germ": {"mode": "germ"}, "bowl_wash": {"mode": "bowl_wash"}, "kill_germ": {"mode": "kill_germ"}, "seafood_wash": {"mode": "seafood_wash"}, "hotpot_wash": {"mode": "hotpot_wash"}, "quietnight_wash": {"mode": "quietnight_wash"}, "less_wash": {"mode": "less_wash"}, "oilnet_wash": {"mode": "oilnet_wash"}, "keep": {"mode": "keep"}, "dry": {"mode": "dry"}}, "local_only": True},
                "softwater": {"options": {"1": {"softwater": 1}, "2": {"softwater": 2}, "3": {"softwater": 3}, "4": {"softwater": 4}, "5": {"softwater": 5}, "6": {"softwater": 6}}},
                "rinse_aid": {"options": {"1": {"bright": 1}, "2": {"bright": 2}, "3": {"bright": 3}, "4": {"bright": 4}, "5": {"bright": 5}}},
                "additional": {"options": {"none": {"additional": 0}, "half_load": {"additional": 7}, "extra_rinse_1": {"additional": 9}, "extra_rinse_2": {"additional": 10}, "strong_wash_func": {"additional": 12}, "half_rinse_1": {"additional": 13}, "half_rinse_2": {"additional": 14}, "door_open_dry": {"additional": 18}, "steam": {"additional": 21}, "speed_up": {"additional": 23}}, "validator": "additional", "mode_dependent": True, "local_only": True},
                "water_level": {"options": {"auto": {"water_level": 0}, "1": {"water_level": 1}, "2": {"water_level": 2}, "3": {"water_level": 3}}, "mode_dependent": True, "local_only": True},
                "water_strong_level": {"options": {"auto": {"water_strong_level": 0}, "1": {"water_strong_level": 1}, "2": {"water_strong_level": 2}}, "mode_dependent": True, "local_only": True},
                "wash_region": {"options": {"all": {"wash_region": 0}, "upper": {"wash_region": 1}, "lower": {"wash_region": 2}}, "mode_dependent": True, "local_only": True},
                "work_time": {"options": {"0": {"work_time": 0}, "1": {"work_time": 1}, "2": {"work_time": 2}, "3": {"work_time": 3}, "4": {"work_time": 4}, "5": {"work_time": 5}, "6": {"work_time": 6}, "7": {"work_time": 7}, "8": {"work_time": 8}, "9": {"work_time": 9}, "10": {"work_time": 10}}, "mode_dependent": True, "local_only": True},
            },
            Platform.SENSOR: {
                "error_code": {"device_class": SensorDeviceClass.ENUM},
                "temperature": {"device_class": SensorDeviceClass.TEMPERATURE, "unit_of_measurement": UnitOfTemperature.CELSIUS, "state_class": SensorStateClass.MEASUREMENT},
                "left_time": {"device_class": SensorDeviceClass.DURATION, "unit_of_measurement": UnitOfTime.MINUTES, "state_class": SensorStateClass.MEASUREMENT},
                "air_left_hour": {"device_class": SensorDeviceClass.DURATION, "unit_of_measurement": UnitOfTime.HOURS, "state_class": SensorStateClass.MEASUREMENT},
                "order_left_time": {"device_class": SensorDeviceClass.DURATION, "unit_of_measurement": UnitOfTime.MINUTES, "state_class": SensorStateClass.MEASUREMENT, "attribute": "order_left_total"},
                "device_status": {"device_class": SensorDeviceClass.ENUM, "computed_status": True},
                "wash_stage": {"device_class": SensorDeviceClass.ENUM}
                }
            }
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# Functions
# ══════════════════════════════════════════════════════════════════════════════

# ── E1 statusNum computation ──

def get_status_num(work_status, airswitch=0, air_left_hour=0, dryswitch=0, keep_start_now=False):
    """Compute statusNum from device attributes."""
    if work_status is None:
        return -3
    num = _WORK_STATUS_NUM.get(work_status, -3)
    if num == 1:
        try:
            if int(dryswitch) == 2:
                num = 6
        except (ValueError, TypeError):
            pass
        try:
            if int(airswitch) != 0 and int(air_left_hour) != 0 and keep_start_now:
                num = 5
        except (ValueError, TypeError):
            pass
    if num == 0:
        try:
            if int(air_left_hour) > 0 and int(airswitch) == 1:
                num = -2
        except (ValueError, TypeError):
            pass
    if num == 10:
        num = 1
    return num


def get_status_text(status_num: int, keep_name: str = "", dry_name: str = "") -> str:
    """Get human-readable status text."""
    if status_num in (-2, 5):
        return f"{keep_name or '保管'}中"
    if status_num == 6:
        return f"{dry_name or '烘干'}中"
    return _STATUS_TEXT.get(status_num, _STATUS_TEXT[-3])


# ── Validators ──

def validate_additional(
    option_key: str, options_map: dict, data: dict, diff_flags: dict,
) -> None:
    """Validate additional select: blocks door_open_dry when keep is active.

    Uses options_map to resolve the option value, matching smart_home's
    implementation which survives cloud config key renames.
    """
    if option_key not in options_map:
        return
    value_map = options_map[option_key]
    if not isinstance(value_map, dict):
        return
    if value_map.get("additional") != 18:
        return
    if not diff_flags.get("additionalSync"):
        return
    try:
        if int(data.get("airswitch", 0)) > 0:
            raise HomeAssistantError("保管功能已开启，请先关闭保管再选择开门速干")
    except (ValueError, TypeError):
        pass


def validate_keep_dry(action: str, data: dict, diff_flags: dict) -> None:
    """Validate keep/dry mutual exclusion."""
    if not diff_flags.get("keepWithoutDry"):
        return
    if action == "dry":
        try:
            if int(data.get("airswitch", 0)) > 0:
                raise HomeAssistantError("保管功能已开启，请先关闭保管")
        except (ValueError, TypeError): pass
    elif action == "keep":
        try:
            if int(data.get("dryswitch", 0)) > 0:
                raise HomeAssistantError("烘干功能已开启，请先关闭烘干")
        except (ValueError, TypeError): pass


def validate_keep_on(data: dict, keep_start_now: bool) -> None:
    """Validate keep requires duration set."""
    if not keep_start_now:
        return
    try:
        if int(data.get("air_set_hour", 0)) == 0:
            raise HomeAssistantError("请先设置保管时长")
    except (ValueError, TypeError):
        pass


def validate_can_operate(
    action: str, data: dict, diff_flags: dict = None,
) -> None:
    """Pre-operation guard: door/lock/error/piping/water."""
    if diff_flags is None:
        diff_flags = {}
    sn = get_status_num(
        data.get("work_status"), airswitch=data.get("airswitch", 0),
        air_left_hour=data.get("air_left_hour", 0), dryswitch=data.get("dryswitch", 0),
    )
    # doorOff devices have unreliable door sensors; skip door check
    if not diff_flags.get("doorOff"):
        if action not in ("power", "cancel") and not data.get("doorswitch"):
            raise HomeAssistantError("门开中，请先关门后操作")
    if data.get("lock") == "on":
        raise HomeAssistantError("童锁中，请先解锁")
    if sn == 4:
        raise HomeAssistantError("设备故障中，请检查")
    if action in ("start", "order") and data.get("work_status") == "pipeInspect":
        raise HomeAssistantError("设备排水中，暂不可控制")
    if action == "start":
        mode = data.get("mode", "")
        if data.get("water_lack") and mode not in ("germ", "keep", "dry"):
            raise HomeAssistantError("缺水中，请检查进水")


async def dispatch_validator(
    validator_name: str, data: dict, diff_flags: dict,
    keep_start_now: bool = False, option: Any = None,
    options_map: dict = None,
) -> None:
    """Unified validator dispatcher."""
    if validator_name in ("keep", "dry"):
        validate_keep_dry(validator_name, data, diff_flags)
    elif validator_name == "keep_on":
        validate_keep_on(data, keep_start_now)
    elif validator_name.startswith("can_operate:"):
        validate_can_operate(validator_name.split(":", 1)[1], data, diff_flags)
    elif validator_name == "additional":
        validate_additional(option or "", options_map or {}, data, diff_flags)


# ── Condition computation ──

def calc_condition_result(
    mode_name: str, mode_conditions: dict, data: dict, bright_condition: bool,
) -> dict:
    """Compute condition-based time/temp/step matching mini-program calcConditionResult."""
    conditions = mode_conditions.get(mode_name)
    if not conditions:
        return {}
    state: dict = {}
    for attr, key in [("additional", "additionalVal"), ("wash_region", "regionVal"),
                       ("water_level", "waterLevelVal"), ("water_strong_level", "waterStrongLevelVal")]:
        v = data.get(attr)
        if v is not None:
            try: state[key] = int(v)
            except (ValueError, TypeError): pass
    for k in ["more_dry_wash", "more_dry"]:
        if k in data:
            state[f"{'moreDryWashVal' if 'wash' in k else 'moreDryVal'}"] = 1 if data.get(k) else 0
    if bright_condition:
        state["brightVal"] = 0 if data.get("bright_lack") else 1
    cond_list = conditions.get("list", [])
    if cond_list and state:
        for item in cond_list:
            cond_map = item.get("condition", {})
            if cond_map and all(state.get(k) == v for k, v in cond_map.items()):
                return dict(item.get("result", {}))
    return dict(conditions.get("default", {}))


# ── Command builders ──

def build_cancel_command(status_num: int) -> dict:
    """Build cancel command dispatching on statusNum."""
    if status_num == 3:
        return {"work_status": "cancel"}
    if status_num == 2:
        return {"work_status": "cancel_order"}
    if status_num == 5:
        return {"airswitch": 0}
    if status_num == 6:
        return {"dryswitch": 0}
    return {}


def build_pause_command(data: dict, status_num: int) -> dict:
    """Build pause/resume command."""
    if status_num not in (2, 3):
        return {}
    return {"operator": "pause"} if data.get("operator") == "start" else {"operator": "start"}


def build_start_command(
    data: dict, status_num: int, diff_flags: dict,
    mode_features: dict = None,
    last_user_mode: str = "",
) -> dict:
    """Build start command matching mini-program operator.js start().

    Path A (statusNum==1, idle): normal start with feature bundling.
    Path B (statusNum==2, order): bypass order, start immediately.
    """
    if status_num not in (1, 2):
        return {}

    # Path B: start immediately from order state
    if status_num == 2:
        mode = data.get("mode", "")
        cmd = {"work_status": "work", "mode": mode}
        for feature in (mode_features or {}).get(mode, set()):
            if feature in ("keep", "dry"):
                continue
            val = data.get(feature)
            if val is not None:
                cmd[feature] = bool(val) if feature == "more_dry_wash" else val
        return cmd

    # Path A: normal idle start
    mode = data.get("mode", "")

    # ── Mode fallback: device may report neutral_gear / "" / invalid in idle ──
    if not mode or not (mode_features or {}).get(mode):
        if last_user_mode and (mode_features or {}).get(last_user_mode):
            mode = last_user_mode
        else:
            valid = [m for m in (mode_features or {}) if m not in ("keep", "dry")]
            mode = valid[0] if valid else ""
    if not mode:
        return {}

    if mode == "keep":
        if diff_flags.get("turnOffOnKeepStart"):
            return {"_action": "cancel_keep_then_start"}
        return {"airswitch": 2}
    if mode == "dry":
        return {"dryswitch": 2}

    cmd: dict = {"work_status": "work", "mode": mode}

    # Bundle feature values filtered by mode_features (data already
    # includes local_only values merged in by button.py).
    supported = (mode_features or {}).get(mode, set())

    for attr in ("additional", "water_level", "water_strong_level"):
        val = data.get(attr)
        if val is not None and attr in supported:
            cmd[attr] = val
    for attr in ("wash_region", "work_time"):
        val = data.get(attr)
        if val is not None and attr in supported:
            try:
                if attr == "wash_region":
                    if int(val) in (1, 2):
                        cmd[attr] = val
                elif int(val) > 0:
                    cmd[attr] = val
            except (ValueError, TypeError):
                pass
    for attr in ("more_dry", "more_dry_wash"):
        val = data.get(attr)
        if val is not None and attr in supported:
            cmd[attr] = val
    if "door_auto_open" in supported:
        val = data.get("door_auto_open")
        if val is not None:
            cmd["door_auto_open"] = 1 if val else 2
    if "auto_throw" in supported and diff_flags.get("autoThrowWithMode"):
        val = data.get("auto_throw")
        if val is not None:
            cmd["auto_throw"] = val
    return cmd


def build_order_command(
    data: dict, diff_flags: dict,
    mode_features: dict = None,
    last_user_mode: str = "",
) -> dict:
    """Build order command with time calculation and feature bundling."""
    mode = data.get("mode", "")
    if mode and mode_features and mode not in mode_features:
        if last_user_mode and last_user_mode in mode_features:
            mode = last_user_mode
        else:
            valid = [m for m in (mode_features or {}) if m not in ("keep", "dry")]
            mode = valid[0] if valid else mode
    target_h = data.get("order_target_hour")
    target_m = data.get("order_target_min")
    delay_h, delay_m = 0, 0
    if target_h is not None and target_m is not None:
        now = _dt.datetime.now()
        now_min = now.hour * 60 + now.minute
        target_min = int(target_h) * 60 + int(target_m)
        if target_min <= now_min:
            target_min += 1440
        total_min = target_min - now_min
        delay_h, delay_m = total_min // 60, total_min % 60
    cmd: dict = {"work_status": "order", "mode": mode}
    if diff_flags.get("minuteOrder"):
        cmd["order_set_hour"] = 0
        cmd["order_set_min"] = delay_h * 60 + delay_m
    else:
        cmd["order_set_hour"] = delay_h
        cmd["order_set_min"] = delay_m

    supported = (mode_features or {}).get(mode, set())
    for attr in ("additional", "water_level", "water_strong_level",
                  "more_dry", "more_dry_wash",
                  "wash_region", "work_time"):
        val = data.get(attr)
        if val is not None and attr in supported:
            if attr == "wash_region":
                try:
                    if int(val) in (1, 2):
                        cmd[attr] = val
                except (ValueError, TypeError):
                    pass
            else:
                cmd[attr] = val
    if "door_auto_open" in supported:
        val = data.get("door_auto_open")
        if val is not None:
            cmd["door_auto_open"] = 1 if val else 2
    if "auto_throw" in supported and diff_flags.get("autoThrowWithMode"):
        val = data.get("auto_throw")
        if val is not None:
            cmd["auto_throw"] = val
    return cmd


def build_keep_command(data: dict, status_num: int, keep_start_now: bool) -> dict:
    """Build keep start/cancel command."""
    if status_num in (1, 2) and keep_start_now:
        return {"airswitch": 2}
    if status_num == 5:
        return {"airswitch": 0}
    return {}


def build_dry_command(data: dict, status_num: int) -> dict:
    """Build dry start/cancel command."""
    if status_num in (1, 2):
        return {"dryswitch": 2}
    if status_num == 6:
        return {"dryswitch": 0}
    return {}


def build_auto_throw_command(data: dict, value: bool) -> dict:
    """Build auto_throw toggle command."""
    return {"auto_throw": 1 if value else 2}


# ── Cloud config helpers ──

def apply_device_config(mapping: dict, device_config: dict, device_type: int = 0, device_version: int = 0) -> dict:
    """Merge cloud-downloaded device config into static mapping."""
    if not device_config or not mapping:
        return mapping
    version_key = f"version_{device_version}"
    if version_key not in device_config:
        version_key = "version_0"
        if version_key not in device_config:
            return mapping
    cfg = device_config[version_key]
    if not isinstance(cfg, dict):
        return mapping
    mode_list = cfg.get("modeList", {})
    settings = cfg.get("setting", {})
    more = cfg.get("more", {})

    result = _json.loads(_json.dumps(mapping))
    entities = dict(result.get("entities", {}))
    sc = dict(entities.get(Platform.SELECT, {}))
    sw = dict(entities.get(Platform.SWITCH, {}))
    lk = dict(entities.get(Platform.LOCK, {}))
    sn = dict(entities.get(Platform.SENSOR, {}))
    nu = dict(entities.get(Platform.NUMBER, {}))
    btn = dict(entities.get(Platform.BUTTON, {}))
    bs = dict(entities.get(Platform.BINARY_SENSOR, {}))

    # 1. Filter wash_mode & use cloud display names
    wm = dict(sc.get("wash_mode", {}))
    if wm and mode_list:
        opts = dict(wm.get("options", {}))
        named: dict[str, dict] = {}
        for mode_key in set(mode_list) & set(opts):
            md = mode_list.get(mode_key, {})
            cloud_name = md.get("name", mode_key) if isinstance(md, dict) else mode_key
            dedup = cloud_name
            suffix = 1
            while dedup in named:
                suffix += 1
                dedup = f"{cloud_name} {suffix}"
            named[dedup] = opts[mode_key]
        if named:
            wm["options"] = named
            sc["wash_mode"] = wm
            _LOGGER.info("Filtered wash_mode: %d modes", len(named))

    # 2. Build dynamic select options
    for eid, (fk, cf) in _DYNAMIC_SELECTS.items():
        if eid not in sc:
            continue
        items: dict[int, str] = {}
        for md in mode_list.values():
            if not isinstance(md, dict):
                continue
            fc = (md.get("more", {}) or {}).get(fk)
            if isinstance(fc, dict):
                for item in fc.get("list") or []:
                    v = item.get("value")
                    if v is not None:
                        items[v] = item.get("name", str(v))
        if items:
            sc[eid]["options"] = {n: {cf: v} for v, n in sorted(items.items())}
            _LOGGER.info("Built %s options from cloud", eid)

    # 3. Build work_time from germ min/max
    if "work_time" in sc:
        w_min, w_max = None, 10
        for md in mode_list.values():
            if isinstance(md, dict):
                gc = (md.get("more", {}) or {}).get("germ")
                if isinstance(gc, dict):
                    if gc.get("min") is not None:
                        v = int(gc["min"])
                        w_min = v if w_min is None else min(w_min, v)
                    if gc.get("max") is not None: w_max = max(w_max, int(gc["max"]))
        if w_min is None:
            w_min = 0
        sc["work_time"]["options"] = {str(m): {"work_time": m} for m in range(w_min, w_max + 1)}

    # 4. Remove unsupported features
    active: set[str] = set()
    _list_f = {"additional", "region", "waterLevel", "waterStrongLevel"}
    for md in mode_list.values():
        if isinstance(md, dict):
            mm = md.get("more", {})
            if isinstance(mm, dict):
                for fk, fv in mm.items():
                    if fk in _list_f and isinstance(fv, dict) and not (fv.get("list") or []):
                        continue
                    active.add(fk)
    if isinstance(more, dict):
        active.update(more.keys())

    missing_features: set[str] = set()
    for fk, (pf, eid) in _FEATURE_MAP.items():
        if fk not in active:
            {"select": sc, "switch": sw}.get(pf, {}).pop(eid, None)
            missing_features.add(eid)
    if "germ" not in active:
        sw.pop("uvswitch", None)
        missing_features.add("uvswitch")

    # 4a. Build per-mode feature availability map (_mode_features)
    mode_features: dict[str, set[str]] = {}
    for mode_name, mode_data in mode_list.items():
        if not isinstance(mode_data, dict):
            continue
        mode_more = mode_data.get("more", {})
        if not isinstance(mode_more, dict):
            continue
        features: list[str] = []
        for fk, (pf, eid) in _FEATURE_MAP.items():
            if fk in mode_more:
                features.append(eid)
        if features:
            mode_features[mode_name] = features
    result["_mode_features"] = mode_features
    if mode_features:
        _LOGGER.info("Per-mode features: %s", list(mode_features.keys()))

    # 4b. Extract per-mode conditions for bright_lack matching
    mode_conditions: dict[str, dict] = {}
    for mode_name, mode_data in mode_list.items():
        if not isinstance(mode_data, dict):
            continue
        conditions = mode_data.get("conditions")
        if isinstance(conditions, dict) and conditions.get("list"):
            mode_conditions[mode_name] = conditions
    if mode_conditions:
        result["_mode_conditions"] = mode_conditions

    # 5. Device-level flags → pop unsupported entities (matching smart_home)
    if more:
        if not more.get("lock"): lk.pop("lock", None)
        if not more.get("bright"): sc.pop("rinse_aid", None)
        salt = more.get("salt", {})
        if isinstance(salt, dict) and not salt.get("enable"): sc.pop("softwater", None)

    # 6. Setting controls → pop unsupported entities
    if settings:
        if not (settings.get("keepStartNow") or settings.get("keepSetTime")):
            sw.pop("airswitch", None)
            nu.pop("air_set_hour", None)
            btn.pop("start_keep", None)
        if not (settings.get("dryStartNow") or settings.get("drySetTime")):
            sw.pop("dryswitch", None)
            nu.pop("dry_set_min", None)
            btn.pop("start_dry", None)
        elif not settings.get("drySetTime"):
            nu.pop("dry_set_min", None)

    # 6a. hasKeepBtn / hasDryBtn detection (mirrors keep.js / dry.js)
    has_keep_btn = "keep" not in mode_list
    if has_keep_btn:
        found = any(
            isinstance(md, dict) and "keep" in (md.get("more", {}) or {})
            for md in mode_list.values()
        )
        has_keep_btn = found
    result["_has_keep_btn"] = has_keep_btn
    if has_keep_btn:
        btn.pop("start_keep", None)
        _LOGGER.info("hasKeepBtn=true — hiding start_keep")
    has_dry_btn = not bool(settings.get("drySetTime", False))
    result["_has_dry_btn"] = has_dry_btn
    if has_dry_btn:
        btn.pop("start_dry", None)
        _LOGGER.info("hasDryBtn=true — hiding start_dry")
    # brightCondition for condition matching
    result["_bright_condition"] = bool(settings.get("brightCondition", False))
    # keepStartNow / keepTimeType — needed by coordinator for status computation + side effects
    result["_keep_start_now"] = bool(settings.get("keepStartNow", 0))
    result["_keep_time_type"] = settings.get("keepTimeType", 0)

    # 7. Extract cloud text names for keep/dry status display
    config_text = cfg.get("text", {})
    if isinstance(config_text, dict):
        kt = config_text.get("keep", {})
        if isinstance(kt, dict) and kt.get("name"):
            result["_keep_text_name"] = kt["name"]
        dt = config_text.get("dry", {})
        if isinstance(dt, dict) and dt.get("name"):
            result["_dry_text_name"] = dt["name"]
        # moreDryWash dynamic cloud name
        mdw = config_text.get("moreDryWash", {})
        if isinstance(mdw, dict) and mdw.get("name") and "more_dry_wash" in sc:
            sc["more_dry_wash"]["cloud_name"] = mdw["name"]

    # 8. Reassemble
    entities[Platform.SELECT] = sc
    entities[Platform.SWITCH] = sw
    entities[Platform.LOCK] = lk
    entities[Platform.SENSOR] = sn
    entities[Platform.NUMBER] = nu
    entities[Platform.BINARY_SENSOR] = bs
    entities[Platform.BUTTON] = btn
    result["entities"] = entities
    return result


def get_default_diff() -> dict:
    """Return the built-in diff config fallback (matching mini-program utils/diff.js)."""
    return _DEFAULT_DIFF
