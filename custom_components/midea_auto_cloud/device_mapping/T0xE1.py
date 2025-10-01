from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
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
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "softwater_lack": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "wash_stage":{
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "bright_lack": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
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
                    }
                },
                "wash_mode": {
                    "options": {
                        "neutral_gear": {"mode": "neutral_gear"},
                        "auto_wash": {"mode": "auto_wash"},
                        "strong_wash": {"mode": "strong_wash"},
                        "standard_wash": {"mode": "standard_wash"},
                        "eco_wash": {"mode": "eco_wash"},
                        "glass_wash": {"mode": "glass_wash"},
                        "hour_wash": {"mode": "hour_wash"},
                        "fast_wash": {"mode": "fast_wash"},
                        "soak_wash": {"mode": "soak_wash"},
                        "90min_wash": {"mode": "90min_wash"},
                        "self_clean": {"mode": "self_clean"},
                        "fruit_wash": {"mode": "fruit_wash"},
                        "self_define": {"mode": "self_define"},
                        "germ": {"mode": "germ"},
                        "bowl_wash": {"mode": "bowl_wash"},
                        "kill_germ": {"mode": "kill_germ"},
                        "seafood_wash": {"mode": "seafood_wash"},
                        "hotpot_wash": {"mode": "hotpot_wash"},
                        "quietnight_wash": {"mode": "quietnight_wash"},
                        "less_wash": {"mode": "less_wash"},
                        "oilnet_wash": {"mode": "oilnet_wash"}
                    }
                },
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
                    "unit_of_measurement": UnitOfTime.HOURS,
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