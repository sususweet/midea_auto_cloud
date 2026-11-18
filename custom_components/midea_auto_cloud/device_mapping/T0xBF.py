from homeassistant.const import Platform, UnitOfTime, UnitOfArea, UnitOfTemperature
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[work_time]",
                    "rvalue": "[work_second] + 60 * [work_minute] + 3600 * [work_hour]"
                },
                {
                    "lvalue": "[set_time]",
                    "rvalue": "[second_set] + 60 * [minute_set] + 3600 * [hour_set]"
                }
            ],
            "set": [
            ]
        },
        "entities": {
            Platform.BINARY_SENSOR: {
                "lack_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "rationale": [0, 1]
                },
                "door_open": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "change_water": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "rationale": [0, 1]
                }
            },
            Platform.SENSOR: {
                "work_status": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "cur_temperature_above": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cur_temperature_underside": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "work_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "set_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    }
}
