from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "upstair_work_status", "downstair_work_status", "middlestair_work_status",
            "upstair_mode", "downstair_mode", "middlestair_mode",
            "upstair_temp", "downstair_temp", "middlestair_temp"
        ],
        "entities": {
            Platform.BINARY_SENSOR: {
                "door_middlestair": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "door_upstair": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "door_downstair": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
                "downstair_ispreheat": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "upstair_ispreheat": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "downstair_iscooling": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "upstair_iscooling": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "middlestair_ispreheat": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "middlestair_iscooling": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                },
                "lock": {
                    "device_class": BinarySensorDeviceClass.LOCK,
                },
                "is_error": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "uv_disinfect": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                }
            },
            Platform.SELECT: {
                "upstair_work_status": {
                    "options": {
                        "power_off": {"upstair_work_status": "power_off"},
                        "power_on": {"upstair_work_status": "power_on"},
                        "working": {"upstair_work_status": "working"},
                        "pause": {"upstair_work_status": "pause"},
                        "finish": {"upstair_work_status": "finish"},
                        "error": {"upstair_work_status": "error"}
                    }
                },
                "downstair_work_status": {
                    "options": {
                        "power_off": {"downstair_work_status": "power_off"},
                        "power_on": {"downstair_work_status": "power_on"},
                        "working": {"downstair_work_status": "working"},
                        "pause": {"downstair_work_status": "pause"},
                        "finish": {"downstair_work_status": "finish"},
                        "error": {"downstair_work_status": "error"}
                    }
                },
                "middlestair_work_status": {
                    "options": {
                        "power_off": {"middlestair_work_status": "power_off"},
                        "power_on": {"middlestair_work_status": "power_on"},
                        "working": {"middlestair_work_status": "working"},
                        "pause": {"middlestair_work_status": "pause"},
                        "finish": {"middlestair_work_status": "finish"},
                        "error": {"middlestair_work_status": "error"}
                    }
                },
                "upstair_mode": {
                    "options": {
                        "off": {"upstair_mode": "0"},
                        "bake": {"upstair_mode": "1"},
                        "roast": {"upstair_mode": "2"},
                        "grill": {"upstair_mode": "3"},
                        "convection": {"upstair_mode": "4"},
                        "defrost": {"upstair_mode": "5"}
                    }
                },
                "downstair_mode": {
                    "options": {
                        "off": {"downstair_mode": "0"},
                        "bake": {"downstair_mode": "1"},
                        "roast": {"downstair_mode": "2"},
                        "grill": {"downstair_mode": "3"},
                        "convection": {"downstair_mode": "4"},
                        "defrost": {"downstair_mode": "5"}
                    }
                },
                "middlestair_mode": {
                    "options": {
                        "off": {"middlestair_mode": "0"},
                        "bake": {"middlestair_mode": "1"},
                        "roast": {"middlestair_mode": "2"},
                        "grill": {"middlestair_mode": "3"},
                        "convection": {"middlestair_mode": "4"},
                        "defrost": {"middlestair_mode": "5"}
                    }
                }
            },
            Platform.SENSOR: {
                "upstair_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "downstair_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "middlestair_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "upstair_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "upstair_min": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "upstair_sec": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "middlestair_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "middlestair_min": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "middlestair_sec": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "downstair_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "downstair_min": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "downstair_sec": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "order_hour": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "order_min": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "order_sec": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "version": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
