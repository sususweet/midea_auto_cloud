from homeassistant.const import Platform, UnitOfTemperature, UnitOfVolume, UnitOfTime, PERCENTAGE, PRECISION_HALVES, \
    UnitOfEnergy, UnitOfPower, PRECISION_WHOLE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": ["warm_target_temp", "boil_target_temp", "meate_select", "max_work_time", "warm_time_min"],
        "entities": {
            Platform.BINARY_SENSOR: {
                "islack_water": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            },
            # Platform.NUMBER: {
            #     "warm_time_min": {
            #         "min": 0,
            #         "max": 480,
            #         "step": 60
            #     },
            #     "max_work_time": {
            #         "min": 0,
            #         "max": 12,
            #         "step": 1
            #     },
            #     "warm_target_temp": {
            #        "min": 0,
            #        "max": 100,
            #        "step": 1
            #     },
            #     "boil_target_temp": {
            #         "min": 0,
            #         "max": 100,
            #         "step": 1
            #     },
            # },
            Platform.SELECT: {
                "work_mode": {
                    "options": {
                        "取消": {"work_mode": "0", "work_switch": "cancel"},
                        "烧水": {"work_mode": "1", "work_switch": "start"},
                        "除氯": {"work_mode": "2", "work_switch": "start"},
                        "花草茶": {"work_mode": "4", "work_switch": "start"},
                        "养生汤": {"work_mode": "5", "work_switch": "start"},
                    }
                }
            },
            Platform.SENSOR: {
                "current_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
