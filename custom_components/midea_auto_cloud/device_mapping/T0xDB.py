from homeassistant.const import Platform, UnitOfElectricPotential, UnitOfTemperature, UnitOfTime
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": [0, 1],
        "calculate": {
            "get": [
                {
                    "lvalue": "[remaining_time]",
                    "rvalue": "[remain_time]"
                }
            ],
            "set": {
            }
        },
        "entities": {
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "softener_lack": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "detergent_lack": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "door_opened": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "bucket_water_overheating": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "memory": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "appointment": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "spray_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "old_speedy": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "nightly": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "down_light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "easy_ironing": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "super_clean_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "intelligent_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "strong_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "silent": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "speedy": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "flocks_switcher": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "fresh_anion_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "dry_weighing_already": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "keep_fresh_status": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "drying_tunnel_overheating": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "fast_clean_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "steam_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "beforehand_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ai_flag": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "water_plus": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "soak": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ultraviolet_lamp": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "eye_wash": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "microbubble": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "wind_dispel": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cycle_memory": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            },
            Platform.SELECT: {
                "running_status": {
                    "options": {
                        "standby": {"running_status": "standby"},
                        "running": {"running_status": "running"},
                        "pause": {"running_status": "pause"},
                        "finish": {"running_status": "finish"},
                        "error": {"running_status": "error"}
                    }
                },
                "db_dehydration_speed": {
                    "options": {
                        "low": {"db_dehydration_speed": "1"},
                        "medium": {"db_dehydration_speed": "2"},
                        "high": {"db_dehydration_speed": "3"},
                        "extra_high": {"db_dehydration_speed": "4"}
                    }
                },
                "mode": {
                    "options": {
                        "normal": {"mode": "normal"},
                        "eco": {"mode": "eco"},
                        "quick": {"mode": "quick"},
                        "heavy": {"mode": "heavy"},
                        "delicate": {"mode": "delicate"}
                    }
                },
                "water_level": {
                    "options": {
                        "low": {"water_level": "low"},
                        "medium": {"water_level": "medium"},
                        "high": {"water_level": "high"},
                        "extra_high": {"water_level": "extra_high"}
                    }
                },
                "program": {
                    "options": {
                        "ssp": {"program": "ssp"},
                        "cotton": {"program": "cotton"},
                        "synthetic": {"program": "synthetic"},
                        "wool": {"program": "wool"},
                        "delicate": {"program": "delicate"},
                        "quick": {"program": "quick"}
                    }
                },
                "temperature": {
                    "options": {
                        "cold": {"temperature": "cold"},
                        "warm": {"temperature": "warm"},
                        "hot": {"temperature": "hot"},
                        "extra_hot": {"temperature": "extra_hot"}
                    }
                },
                "detergent_density": {
                    "options": {
                        "low": {"detergent_density": "low"},
                        "medium": {"detergent_density": "medium"},
                        "high": {"detergent_density": "high"},
                        "extra_high": {"detergent_density": "extra_high"}
                    }
                },
                "softener_density": {
                    "options": {
                        "low": {"softener_density": "low"},
                        "medium": {"softener_density": "medium"},
                        "high": {"softener_density": "high"},
                        "extra_high": {"softener_density": "extra_high"}
                    }
                },
                "detergent": {
                    "options": {
                        "none": {"detergent": "none"},
                        "little": {"detergent": "little"},
                        "normal": {"detergent": "normal"},
                        "more": {"detergent": "more"}
                    }
                },
                "softener": {
                    "options": {
                        "none": {"softener": "none"},
                        "little": {"softener": "little"},
                        "normal": {"softener": "normal"},
                        "more": {"softener": "more"}
                    }
                },
                "season": {
                    "options": {
                        "spring": {"season": "spring"},
                        "summer": {"season": "summer"},
                        "autumn": {"season": "autumn"},
                        "winter": {"season": "winter"}
                    }
                },
                "disinfectant": {
                    "options": {
                        "none": {"disinfectant": "none"},
                        "light": {"disinfectant": "light"},
                        "medium": {"disinfectant": "medium"},
                        "strong": {"disinfectant": "strong"}
                    }
                },
                "dirty_degree": {
                    "options": {
                        "light": {"dirty_degree": "light"},
                        "medium": {"dirty_degree": "medium"},
                        "heavy": {"dirty_degree": "heavy"},
                        "extra_heavy": {"dirty_degree": "extra_heavy"}
                    }
                },
                "stains": {
                    "options": {
                        "none": {"stains": "none"},
                        "light": {"stains": "light"},
                        "medium": {"stains": "medium"},
                        "heavy": {"stains": "heavy"}
                    }
                },
                "add_rinse": {
                    "options": {
                        "none": {"add_rinse": "none"},
                        "one": {"add_rinse": "one"},
                        "two": {"add_rinse": "two"},
                        "three": {"add_rinse": "three"}
                    }
                },
                "soak_count": {
                    "options": {
                        "none": {"soak_count": "none"},
                        "one": {"soak_count": "one"},
                        "two": {"soak_count": "two"},
                        "three": {"soak_count": "three"}
                    }
                }
            },
            Platform.SENSOR: {
                "wash_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "appointment_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "remain_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "dryer": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "remote_control_flag": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "progress": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_low": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_high": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai1": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai2": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai3": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai4": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai_time1": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "dehydration_time_value": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai_time3": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai_time4": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "customize_machine_cycle": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "detergent_global": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "softener_global": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "detergent_density_global": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "softener_density_global": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "fresh_air_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "flocks_remind_period": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "device_software_version": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "expert_step": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "error_code": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "flocks_wash_count": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "active_oxygen": {
                    "device_class": SensorDeviceClass.ENUM,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "dehydration_time": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "cloud_cycle_jiepai_time2": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "wash_time_value": {
                    "device_class": SensorDeviceClass.DURATION,
                    "unit_of_measurement": UnitOfTime.MINUTES,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    }
}
