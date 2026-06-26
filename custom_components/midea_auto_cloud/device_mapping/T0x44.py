from homeassistant.const import (
    Platform,
    PERCENTAGE, PRECISION_WHOLE, UnitOfTime, UnitOfTemperature,
)
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

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
                    # The thermostat/app lock fan speed while the hvac mode is
                    # auto (the unit manages airflow itself), so hide the
                    # fan-mode control on the climate card in that mode.
                    "fan_lock_hvac_modes": ["auto"],
                    "target_temperature": "temperature",
                    # In auto mode the thermostat controls to a low/high range
                    # (the control_function limits, same as the number entities),
                    # not the single "temperature" setpoint.
                    "target_temperature_low": "control_function_set_temperature_lower_limit",
                    "target_temperature_high": "control_function_set_temperature_upper_limit",
                    "range_hvac_modes": ["auto"],
                    "current_temperature": "screen_temperature_sensor_value",
                    "aux_heat": "ptc",
                    "min_temp": "set_temperature_lower_limit",
                    "max_temp": "set_temperature_upper_limit",
                    "temperature_unit": "temperature_unit",
                    "precision": PRECISION_WHOLE,
                    # Surface running/idle on the climate card via hvac_action.
                    # Direction in auto mode: auto_mode_actual_operating_status
                    # (1 = cooling, 2 = heating), confirmed against the Midea app.
                    "action_compressor": "outdoor_compressor_operating_status",
                    "action_fan": "indoor_fan_run_status",
                    "action_direction": "auto_mode_actual_operating_status",
                },
            },
            Platform.BINARY_SENSOR: {
                # 0 = idle, 1 = running (generic binary sensor: on when value == 1)
                "outdoor_compressor_operating_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "name": "Compressor",
                },
                "indoor_fan_run_status": {
                    "device_class": BinarySensorDeviceClass.RUNNING,
                    "name": "Indoor Fan",
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

