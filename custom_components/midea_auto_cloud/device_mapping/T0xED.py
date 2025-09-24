from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, UnitOfTime, UnitOfElectricPotential, UnitOfVolume, UnitOfMass
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
                "holiday_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_way": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "soften": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "leak_water_protection": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cl_sterilization": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "micro_leak": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "low_salt": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "no_salt": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "low_battery": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "salt_level_sensor_error": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "flowmeter_error": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "leak_water": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "micro_leak_protection": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "maintenance_reminder_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "rsj_stand_by": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "regeneration": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "pre_regeneration": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.BINARY_SENSOR: {
                "maintenance_remind": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "chlorine_sterilization_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "rtc_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            },
            Platform.SENSOR: {
                "micro_leak_protection_value": {
                    "device_class": SensorDeviceClass.PRESSURE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "regeneration_current_stages": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_hardness": {
                    "device_class": SensorDeviceClass.WATER,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "timing_regeneration_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "real_time_setting_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "timing_regeneration_min": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "regeneration_left_seconds": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "maintenance_reminder_setting": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "mixed_water_gear": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "use_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "days_since_last_regeneration": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "velocity": {
                    "device_class": SensorDeviceClass.SPEED,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "supply_voltage": {
                    "device_class": SensorDeviceClass.VOLTAGE,
                    "unit_of_measurement": UnitOfElectricPotential.VOLT,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "left_salt": {
                    "device_class": SensorDeviceClass.WEIGHT,
                    "unit_of_measurement": UnitOfMass.KILOGRAMS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pre_regeneration_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "flushing_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "salt_setting": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "regeneration_count": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "battery_voltage": {
                    "device_class": SensorDeviceClass.VOLTAGE,
                    "unit_of_measurement": UnitOfElectricPotential.VOLT,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "days_since_last_two_regeneration": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "remind_maintenance_days": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.DAYS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "real_date_setting_year": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "real_date_setting_month": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "real_date_setting_day": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "category": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "real_time_setting_min": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "regeneration_stages": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "soft_available_big": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": UnitOfVolume.LITERS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_consumption_big": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": UnitOfVolume.LITERS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_consumption_today": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": UnitOfVolume.LITERS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_consumption_average": {
                    "device_class": SensorDeviceClass.VOLUME,
                    "unit_of_measurement": UnitOfVolume.LITERS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "salt_alarm_threshold": {
                    "device_class": SensorDeviceClass.WEIGHT,
                    "unit_of_measurement": UnitOfMass.KILOGRAMS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "leak_water_protection_value": {
                    "device_class": SensorDeviceClass.PRESSURE,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
