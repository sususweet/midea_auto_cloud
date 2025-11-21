from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform, UnitOfElectricPotential, UnitOfTemperature, UnitOfTime, UnitOfPressure
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "entities": {
            Platform.SWITCH: {
                "winter_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "summer_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SENSOR: {
                "heat_exchanger": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "fan_type": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "ignitor_output": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "fan_output": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "current_heat_set_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "current_bath_set_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "heat_out_water_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "bath_out_water_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "water_gage": {
                    "unit_of_measurement": UnitOfPressure.PA,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            },
            Platform.BINARY_SENSOR: {
                "heating_work": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
                "bathing_work": {
                    "device_class": BinarySensorDeviceClass.RUNNING
                },
            },
        }
    }
}
