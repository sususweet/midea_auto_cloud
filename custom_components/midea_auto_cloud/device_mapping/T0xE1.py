from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": [],
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
                "doorswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dryswitch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dry_step_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.BINARY_SENSOR: {
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
                    "device_class": SensorDeviceClass.ILLUMINANCE,
                    "unit_of_measurement": "lx",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "softwater": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_set_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_left_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    }
}