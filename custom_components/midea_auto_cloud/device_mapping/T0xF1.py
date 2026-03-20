from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": ["power", "work_mode", "speed", "code_id"],
        "calculate": {
            # Device reports power state via `power_on_flag` (0/1), but lua control expects `power` ("off"/"on").
            # So we derive `power` from `power_on_flag` for the SWITCH entity to read.
            "get": [
                {
                    "lvalue": "[power]",
                    "rvalue": "'on' if str([power_on_flag]) == '1' else 'off'",
                }
            ]
        },
        "entities": {
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["off", "on"],
                },
            },
            Platform.SELECT: {
                "work_mode": {
                    "options": {
                        "0": {"work_mode": "0"},
                        "1": {"work_mode": "1"},
                        "2": {"work_mode": "2"},
                        "3": {"work_mode": "3"},
                        "4": {"work_mode": "4"},
                        "5": {"work_mode": "5"},
                        "6": {"work_mode": "6"},
                        "7": {"work_mode": "7"},
                        "8": {"work_mode": "8"},
                        "9": {"work_mode": "9"},
                        "10": {"work_mode": "10"},
                    }
                },
                "speed": {
                    "options": {
                        "0": {"speed": "0"},
                        "1": {"speed": "1"},
                        "2": {"speed": "2"},
                        "3": {"speed": "3"},
                        "4": {"speed": "4"},
                        "5": {"speed": "5"},
                        "6": {"speed": "6"},
                        "7": {"speed": "7"},
                        "8": {"speed": "8"},
                    }
                },
            },
            Platform.SENSOR: {
                "current_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "current_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "work_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "work_stage": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "step_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "cup_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "lid_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "response_type": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "power_on_flag": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "appoint_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "set_work_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "set_keep_warm_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.SECONDS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "set_work_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "set_keep_warm_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
            },
        },
    }
}

