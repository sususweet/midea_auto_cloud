from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime, PERCENTAGE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.components.humidifier import HumidifierDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.SWITCH: {
                "disinfect_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "netIons_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "netions_on_off"
                },
                "airDry_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "airdry_on_off"
                },
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "buzzer": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "display_on_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.BINARY_SENSOR: {
                "add_water_flag": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                },
                "tank_status": {
                    "device_class": BinarySensorDeviceClass.PROBLEM
                },
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
                        "auto": {"humidity_mode": "auto"},
                        "sleep": {"humidity_mode": "sleep"},
                        "continue": {"humidity_mode": "continue"},
                        "parlour": {"humidity_mode": "parlour"},
                        "bedroom": {"humidity_mode": "bedroom"},
                        "kitchen": {"humidity_mode": "kitchen"},
                        "moist_skin": {"humidity_mode": "moist_skin"},
                    }
                }
            },
            Platform.SELECT: {
                "power_on_time": {
                    "options": {
                        "off": {"power_on_timer": "off"},
                        "15": {"power_on_timer": "on", "time_on": "15"},
                        "30": {"power_on_timer": "on", "time_on": "30"},
                        "45": {"power_on_timer": "on", "time_on": "45"},
                        "60": {"power_on_timer": "on", "time_on": "60"},
                    }
                },
                "power_off_time": {
                    "options": {
                        "off": {"power_off_timer": "off"},
                        "15": {"power_off_timer": "on", "time_off": "15"},
                        "30": {"power_off_timer": "on", "time_off": "30"},
                        "45": {"power_off_timer": "on", "time_off": "45"},
                        "60": {"power_off_timer": "on", "time_off": "60"},
                    }
                },
                "wind_gear": {
                    "options": {
                        "lowest": {"wind_gear": "lowest"},
                        "low": {"wind_gear": "low"},
                        "middle": {"wind_gear": "middle"},
                        "high": {"wind_gear": "high"},
                        "auto": {"wind_gear": "auto"},
                    }
                },
                "wind_speed": {
                    "options": {
                        "lowest": {"wind_speed": "lowest"},
                        "low": {"wind_speed": "low"},
                        "middle": {"wind_speed": "middle"},
                        "high": {"wind_speed": "high"},
                        "auto": {"wind_speed": "auto"},
                    }
                },
                "light_color": {
                    "options": {
                        "warm": {"light_color": "warm"},
                        "blue": {"light_color": "blue"},
                        "green": {"light_color": "green"},
                        "red": {"light_color": "red"},
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
            }
        }
    }
}
