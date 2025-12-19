from homeassistant.const import Platform, UnitOfTime, UnitOfArea, CONCENTRATION_PARTS_PER_MILLION, \
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, UnitOfTemperature, UnitOfElectricPotential
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "calculate": {
            "get": [
                {
                    "lvalue": "[indoor_temperature]",
                    "rvalue": "float([temperature]) / 10"
                },
            ],
        },
        "centralized": [],
        "entities": {
            Platform.SENSOR: {
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "humidity": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "co2_value": {
                    "device_class": SensorDeviceClass.CO2,
                    "unit_of_measurement": CONCENTRATION_PARTS_PER_MILLION,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "co2"
                },
                "pm10_value": {
                    "device_class": SensorDeviceClass.PM10,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "pm10"
                },
                "pm25_value": {
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "pm25"
                },
                "voltage": {
                    "device_class": SensorDeviceClass.VOLTAGE,
                    "unit_of_measurement": UnitOfElectricPotential.VOLT,
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    }
}
