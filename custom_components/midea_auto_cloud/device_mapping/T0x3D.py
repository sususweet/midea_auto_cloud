from homeassistant.const import Platform, UnitOfTemperature, UnitOfVolume, UnitOfTime, PERCENTAGE, PRECISION_HALVES, \
    UnitOfEnergy, UnitOfPower, PRECISION_WHOLE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "work_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ['cancel', 'work']
                }
            },
            Platform.SELECT: {
                "warm_target_temp": {
                    "options": {
                        "45℃": {"warm_target_temp": "45"},
                        "55℃": {"warm_target_temp": "55"},
                        "65℃": {"warm_target_temp": "65"},
                        "75℃": {"warm_target_temp": "75"},
                        "85℃": {"warm_target_temp": "85"}
                    }
                },
                "boil_target_temp": {
                    "options": {
                        "45℃": {"boil_target_temp": "45"},
                        "55℃": {"boil_target_temp": "55"},
                        "65℃": {"boil_target_temp": "65"},
                        "75℃": {"boil_target_temp": "75"},
                        "85℃": {"boil_target_temp": "85"}
                    }
                }
            },
            Platform.SENSOR: {
                "cur_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
