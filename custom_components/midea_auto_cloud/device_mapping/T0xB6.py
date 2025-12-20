from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform, UnitOfElectricPotential
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": ["lightness"],
        "calculate": {
            "get": [
                {
                    "lvalue": "[b7_vbattery]",
                    "rvalue": "float([b7_vbatt] / 1000.0)"
                },
            ],
        },
        "entities": {
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wisdom_wind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SENSOR: {
                "b7_left_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "left_status",
                },
                "b7_right_status": {
                    "device_class": SensorDeviceClass.ENUM,
                    "translation_key": "right_status",
                },
                "b7_vbattery":{
                    "device_class": SensorDeviceClass.VOLTAGE,
                    "unit_of_measurement": UnitOfElectricPotential.VOLT,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "battery_voltage",
                }
            },
            Platform.BUTTON: {
                "light_off": {
                    "command": {"electronic_control_version": 2, "type": "b6", "b6_action": "setting",
                                "setting": "light", "light": "off"},
                },
                "light_on": {
                    "command": {"electronic_control_version": 2, "type": "b6", "b6_action": "setting",
                                "setting": "light", "light": "on"},
                },
                "left_stove_off": {
                    "command": {"electronic_control_version": 2, "type": "b7", "b7_work_burner_control": 1,
                                "b7_function_control": 1},
                },
                "right_stove_off": {
                    "command": {"electronic_control_version": 2, "type": "b7", "b7_work_burner_control": 2,
                                "b7_function_control": 1},
                },
                "middle_stove_off": {
                    "command": {"electronic_control_version": 2, "type": "b7", "b7_work_burner_control": 3,
                                "b7_function_control": 1},
                }
            },
            Platform.SELECT: {
                "wind_pressure": {
                    "options": {
                        "off": {"wind_pressure": "0"},
                        "low": {"wind_pressure": "1"},
                        "medium": {"wind_pressure": "2"},
                        "high": {"wind_pressure": "3"},
                        "extreme": {"wind_pressure": "4"},
                    }
                },
                "gear": {
                    "options": {
                        "off": {"gear": 0},
                        "low": {"gear": 1},
                        "medium": {"gear": 2},
                        "high": {"gear": 3},
                        "extreme": {"gear": 4},
                    }
                },
            },
        }
    }
}
