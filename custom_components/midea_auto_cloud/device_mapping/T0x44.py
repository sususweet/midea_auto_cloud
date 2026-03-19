from homeassistant.const import (
    Platform,
    PERCENTAGE, PRECISION_WHOLE, UnitOfTime, UnitOfTemperature,
)
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "auto": {"power": "on", "mode": 1},
                        "cool": {"power": "on", "mode": 2},
                        "dry": {"power": "on", "mode": 3},
                        "heat": {"power": "on", "mode": 4},
                        "fan_only": {"power": "on", "mode": 5},
                    },
                    "preset_modes": {
                        "none": {
                            "eco": "off",
                            "strong_wind": "off",
                        },
                        "eco": {"eco": "on"},
                        "boost": {"strong_wind": "on"},
                    },
                    # "swing_modes": {
                    #     "off": {"horizontal_swing_wind": 0, "vertical_swing_wind": 0},
                    #     "both": {"horizontal_swing_wind": 1, "vertical_swing_wind": 1},
                    #     "horizontal": {"horizontal_swing_wind": 1, "vertical_swing_wind": 0},
                    #     "vertical": {"horizontal_swing_wind": 0, "vertical_swing_wind": 1},
                    # },
                    "fan_modes": {
                        "low": {"wind_speed": 30},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 90},
                        "auto": {"wind_speed": 102},
                    },
                    "target_temperature": "temperature",
                    "current_temperature": "screen_temperature_sensor_value",
                    "aux_heat": "ptc",
                    "min_temp": "set_temperature_lower_limit",
                    "max_temp": "set_temperature_upper_limit",
                    "temperature_unit": "temperature_unit",
                    "precision": PRECISION_WHOLE,
                },
            },
            Platform.SELECT: {
                "dry_time_interval": {
                    "options": {
                        "15min": {"dry_time_interval": 15},
                        "30min": {"dry_time_interval": 30},
                        "45min": {"dry_time_interval": 45},
                        "60min": {"dry_time_interval": 60},
                    },
                },
            },
            Platform.NUMBER: {
                "auto_temperature_lower_limit": {
                    "attribute": "control_function_set_temperature_lower_limit",
                    "min": "set_temperature_lower_limit",
                    "max": "set_temperature_upper_limit",
                    "step": 1,
                },
                "auto_temperature_upper_limit": {
                    "attribute": "control_function_set_temperature_upper_limit",
                    "min": "set_temperature_lower_limit",
                    "max": "set_temperature_upper_limit",
                    "step": 1,
                },
            },
            Platform.SWITCH: {
                "eco": {"device_class": SwitchDeviceClass.SWITCH},
                "ptc": {"device_class": SwitchDeviceClass.SWITCH},
                "digital_display": {"device_class": SwitchDeviceClass.SWITCH},
                "voice_control": {"device_class": SwitchDeviceClass.SWITCH},
                "voice_control_speaking": {"device_class": SwitchDeviceClass.SWITCH},
                "mute_voice": {"device_class": SwitchDeviceClass.SWITCH},
            },
            Platform.SENSOR: {
                "dry_remain_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "screen_temperature_sensor_value": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "dynamic_unit": "temperature_unit",
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "indoor_temperature",
                },
                "screen_humidity_sensor_value": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "translation_key": "indoor_humidity"
                },
            },
        },
    },
    "115PD077": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {}
    }
}

