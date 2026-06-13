"""Unified cloud statistics: AC electricity, washer/dishwasher water & power."""

from homeassistant.const import Platform, UnitOfEnergy, UnitOfVolume
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass

_ELECTRICITY_SENSORS = {
    "cloud_electricity_month": {
        "attribute": "cloud_electricity_month",
        "device_class": SensorDeviceClass.ENERGY,
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_electricity_month",
    },
    "cloud_electricity_year": {
        "attribute": "cloud_electricity_year",
        "device_class": SensorDeviceClass.ENERGY,
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_electricity_year",
    },
}

_WATER_POWER_SENSORS = {
    "cloud_water_month": {
        "attribute": "cloud_water_month",
        "device_class": SensorDeviceClass.WATER,
        "unit_of_measurement": UnitOfVolume.LITERS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_water_month",
    },
    "cloud_water_year": {
        "attribute": "cloud_water_year",
        "device_class": SensorDeviceClass.WATER,
        "unit_of_measurement": UnitOfVolume.LITERS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_water_year",
    },
    "cloud_power_month": {
        "attribute": "cloud_power_month",
        "device_class": SensorDeviceClass.ENERGY,
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_power_month",
    },
    "cloud_power_year": {
        "attribute": "cloud_power_year",
        "device_class": SensorDeviceClass.ENERGY,
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_power_year",
    },
}

_WATER_POWER_SENSORS_DUAL = {
    "cloud_water_month_da": {
        "attribute": "cloud_water_month_da",
        "device_class": SensorDeviceClass.WATER,
        "unit_of_measurement": UnitOfVolume.LITERS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_water_month_da",
    },
    "cloud_water_month_db": {
        "attribute": "cloud_water_month_db",
        "device_class": SensorDeviceClass.WATER,
        "unit_of_measurement": UnitOfVolume.LITERS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_water_month_db",
    },
    "cloud_water_year_da": {
        "attribute": "cloud_water_year_da",
        "device_class": SensorDeviceClass.WATER,
        "unit_of_measurement": UnitOfVolume.LITERS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_water_year_da",
    },
    "cloud_water_year_db": {
        "attribute": "cloud_water_year_db",
        "device_class": SensorDeviceClass.WATER,
        "unit_of_measurement": UnitOfVolume.LITERS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_water_year_db",
    },
    "cloud_power_month_da": {
        "attribute": "cloud_power_month_da",
        "device_class": SensorDeviceClass.ENERGY,
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_power_month_da",
    },
    "cloud_power_month_db": {
        "attribute": "cloud_power_month_db",
        "device_class": SensorDeviceClass.ENERGY,
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_power_month_db",
    },
    "cloud_power_year_da": {
        "attribute": "cloud_power_year_da",
        "device_class": SensorDeviceClass.ENERGY,
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_power_year_da",
    },
    "cloud_power_year_db": {
        "attribute": "cloud_power_year_db",
        "device_class": SensorDeviceClass.ENERGY,
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "translation_key": "cloud_power_year_db",
    },
}

# device_type -> cloud_queries + sensors injected into mapping
_CLOUD_STATS_REGISTRY: dict[int, dict] = {
    0xAC: {
        "cloud_queries": {
            "electricity": {"interval": 300},
        },
        "sensors": _ELECTRICITY_SENSORS,
    },
    0xD9: {
        "cloud_queries": {
            "water_power": {"interval": 300, "dual_drum": True},
        },
        "sensors": _WATER_POWER_SENSORS_DUAL,
    },
    0xDA: {
        "cloud_queries": {
            "water_power": {"interval": 300},
        },
        "sensors": _WATER_POWER_SENSORS,
    },
    0xDB: {
        "cloud_queries": {
            "water_power": {"interval": 300},
        },
        "sensors": _WATER_POWER_SENSORS,
    },
    0xE1: {
        "cloud_queries": {
            "water_power": {"interval": 300},
        },
        "sensors": _WATER_POWER_SENSORS,
    },
}


def merge_cloud_stats_mapping(mapping: dict, device_type: int) -> dict:
    """按设备类型合并云端统计查询与传感器到 mapping。"""
    stats = _CLOUD_STATS_REGISTRY.get(device_type)
    if not stats or not mapping:
        return mapping

    merged = {**mapping}
    merged["cloud_queries"] = {
        **stats["cloud_queries"],
        **(mapping.get("cloud_queries") or {}),
    }
    entities = {**(mapping.get("entities") or {})}
    sensors = {
        **(entities.get(Platform.SENSOR) or {}),
        **stats["sensors"],
    }
    entities[Platform.SENSOR] = sensors
    merged["entities"] = entities
    return merged
