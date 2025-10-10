from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.components.humidifier import HumidifierDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power", "disinfect_on_off", "netIons_on_off", "airDry_on_off",
            "wind_gear", "wind_speed", "light_color", "bright_led",
            "humidity_mode", "tank_status", "humidity", "cur_humidity"
        ],
        "entities": {
            Platform.SWITCH: {
                "netIons_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "airDry_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "buzzer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "power_on_timer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "power_off_timer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.BINARY_SENSOR: {
                "add_water_flag": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                }
            },
            Platform.HUMIDIFIER: {
                "humidifier": {
                    "device_class": HumidifierDeviceClass.HUMIDIFIER,
                    "power": "power",
                    "target_humidity": "humidity",
                    "current_humidity": "cur_humidity",
                    "min_humidity": 30,
                    "max_humidity": 80,
                    "mode": "humidity_mode",
                    "modes": {
                        "manual": {"humidity_mode": "manual"},
                        "moist_skin": {"humidity_mode": "moist_skin"},
                        "sleep": {"humidity_mode": "sleep"}
                    }
                }
            },
            Platform.SELECT: {
                "humidity_mode": {
                    "options": {
                        "manual": {"humidity_mode": "manual"},
                        "moist_skin": {"humidity_mode": "moist_skin"},
                        "sleep": {"humidity_mode": "sleep"}
                    }
                },
                "wind_gear": {
                    "options": {
                        "low": {"wind_gear": "low"},
                        "medium": {"wind_gear": "medium"},
                        "high": {"wind_gear": "high"},
                        "auto": {"wind_gear": "auto"},
                        "invalid": {"wind_gear": "invalid"}
                    }
                },
                "wind_speed": {
                    "options": {
                        "low": {"wind_speed": "low"},
                        "medium": {"wind_speed": "medium"},
                        "high": {"wind_speed": "high"},
                        "auto": {"wind_speed": "auto"},
                        "invalid": {"wind_speed": "invalid"}
                    }
                },
                "light_color": {
                    "options": {
                        "warm": {"light_color": "warm"},
                        #"cool": {"light_color": "cool"},
                        #"white": {"light_color": "white"},
                        #"blue": {"light_color": "blue"},
                        #"green": {"light_color": "green"},
                        #"red": {"light_color": "red"},
                        "off": {"light_color": "off"}
                    }
                },
                "bright_led": {
                    "options": {
                        "light": {"bright_led": "light"},
                        "dark": {"bright_led": "dark"},
                        "exit": {"bright_led": "exit"}
                    }
                }
            },
            Platform.SENSOR: {
                "running_percent": {
                    "device_class": SensorDeviceClass.POWER_FACTOR,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM
                },
                "cur_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sensor_battery": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sensor_humidify": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "sensor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "air_dry_left_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "time_on": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "time_off": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "tank_status": {
                    "device_class": SensorDeviceClass.POWER_FACTOR,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}