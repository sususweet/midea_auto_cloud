from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, UnitOfElectricPotential, \
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
    }
}
