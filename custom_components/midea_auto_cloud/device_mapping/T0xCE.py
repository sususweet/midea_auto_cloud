from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power", "mode_state", "fan_set", "room_temp_value", "humidity_set"
        ],
        "entities": {
            Platform.SWITCH: {
                "lock_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "esp_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "passby_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "preheat_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "remain_able": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "hcho_check_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "co2_check_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "function_set_link": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "function_set_sleep": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "function_set_energy_save": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "function_set_prheat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "function_set_ultimate": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "clean_net_clean_flg": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "change_net_change_flg": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "condensation_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "humidity_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "preheat_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "esp_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "pm25_check_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "timer_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "freeze_state": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "humidity_check_enable": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "mode_state": {
                    "options": {
                        "passby": {"mode_state": "passby"},
                        "auto": {"mode_state": "auto"},
                        "manual": {"mode_state": "manual"},
                        "sleep": {"mode_state": "sleep"},
                        "energy_save": {"mode_state": "energy_save"},
                        "ultimate": {"mode_state": "ultimate"}
                    }
                },
                "fan_set": {
                    "options": {
                        "off": {"fan_set": "0"},
                        "low": {"fan_set": "1"},
                        "medium": {"fan_set": "2"},
                        "high": {"fan_set": "3"},
                        "auto": {"fan_set": "4"}
                    }
                }
            },
            Platform.SENSOR: {
                "room_temp_value": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "clean_net_used_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "change_net_used_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "tvoc_value": {
                    "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                    "unit_of_measurement": "mg/m³",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "change_set_real_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "clean_set_real_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "humidity_set": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "room_aqi_value": {
                    "device_class": SensorDeviceClass.AQI,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "change_net_set_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "clean_net_set_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.HOURS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "humidity_value": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "hcho_value": {
                    "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                    "unit_of_measurement": "mg/m³",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "pm25_value": {
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": "µg/m³",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "co2_value": {
                    "device_class": SensorDeviceClass.CO2,
                    "unit_of_measurement": "ppm",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "machine_type": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
