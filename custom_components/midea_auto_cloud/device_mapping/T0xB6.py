from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform, PERCENTAGE, UnitOfTime, UnitOfElectricPotential
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
                "light": {
                    "options": {
                        "off": {"light": "off"},
                        "on": {"light": "on"}
                    },
                    "command": {
                        "electronic_control_version": 2,
                        "type": "b6",
                        "b6_action": "setting",
                        "setting": "light"
                    }
                }
            },
        }
    },
    "730007H8": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": ["lightness"],
        "calculate": {
            "get": [
                {
                    "lvalue": "[b7_vbattery]",
                    "rvalue": "float([b7_vbatt] / 1000.0)"
                },
                {
                    "lvalue": "[total_energy_consumption]",
                    "rvalue": "float([total_working_time] / 60 * 0.14)"
                }
            ],
        },
        "entities": {
            Platform.SWITCH: {
                "power": {
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
                },
                "total_working_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.TOTAL_INCREASING,
                },
                "total_energy_consumption": {
                    "device_class": SensorDeviceClass.ENERGY,
                    "unit_of_measurement": "kWh",
                    "state_class": SensorStateClass.TOTAL_INCREASING,
                }
            },
            Platform.BUTTON: {
                "left_stove_off": {
                    "command": {"electronic_control_version": 2, "type": "b7", "b7_work_burner_control": 1,
                                "b7_function_control": 1},
                },
                "right_stove_off": {
                    "command": {"electronic_control_version": 2, "type": "b7", "b7_work_burner_control": 2,
                                "b7_function_control": 1},
                }
            },
            Platform.NUMBER: {
                "lightness": {
                    "min": 10,
                    "max": 100,
                    "step": 5,
                    "command": {
                        "electronic_control_version": 2,
                        "type": "b6",
                        "b6_action": "setting",
                        "setting": "light",
                        "lightness": "{value}"
                    }
                }
            },
            Platform.SELECT: {
                "gear": {
                    "options": {
                        "off": {"gear": 0},
                        "low": {"gear": 1},
                        "medium": {"gear": 2},
                        "high": {"gear": 3},
                        "extreme": {"gear": 4},
                    }
                },
                "gesture": {
                    "options": {
                        "off": {"gesture": "off"},
                        "on": {"gesture": "on"}
                    },
                    "command": {
                        "electronic_control_version": 2,
                        "type": "b6",
                        "b6_action": "setting",
                        "setting": "gesture"
                    }
                },
                "gesture_value": {
                    "options": {
                        "开关机": {"gesture_value": 1},
                        "调风速": {"gesture_value": 2},
                        "开关灯": {"gesture_value": 3},
                        "开关机+调风速": {"gesture_value": 4}
                    },
                    "command": {
                        "electronic_control_version": 2,
                        "type": "b6",
                        "b6_action": "setting",
                        "setting": "gesture"
                    }
                },
                "gesture_sensitivity_value": {
                    "options": {
                        "low": {"gesture_sensitivity_value": 1},
                        "medium": {"gesture_sensitivity_value": 2},
                        "high": {"gesture_sensitivity_value": 3}
                    },
                    "command": {
                        "electronic_control_version": 2,
                        "type": "b6",
                        "b6_action": "setting",
                        "setting": "gesture"
                    }
                },
                "inverter": {
                    "options": {
                        "off": {"inverter": "off"},
                        "on": {"inverter": "on"}
                    },
                    "command": {
                        "electronic_control_version": 2,
                        "type": "b6",
                        "b6_action": "control"
                    }
                },
                "light": {
                    "options": {
                        "off": {"light": "off"},
                        "on": {"light": "on"}
                    },
                    "command": {
                        "electronic_control_version": 2,
                        "type": "b6",
                        "b6_action": "setting",
                        "setting": "light"
                    }
                }
            }
        }
    }
}
