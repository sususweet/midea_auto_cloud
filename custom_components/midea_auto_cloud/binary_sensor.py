from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass
)
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .midea_entity import MideaEntity
from . import load_device_config


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities for Midea devices."""
    account_bucket = hass.data.get(DOMAIN, {}).get("accounts", {}).get(config_entry.entry_id)
    if not account_bucket:
        async_add_entities([])
        return
    device_list = account_bucket.get("device_list", {})
    coordinator_map = account_bucket.get("coordinator_map", {})

    devs = []
    for device_id, info in device_list.items():
        device_type = info.get("type")
        sn8 = info.get("sn8")
        config = await load_device_config(hass, device_type, sn8) or {}
        entities_cfg = (config.get("entities") or {}).get(Platform.BINARY_SENSOR, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        # 连接状态实体
        if coordinator and device:
            devs.append(MideaDeviceStatusSensorEntity(coordinator, device, manufacturer, rationale, "Status", {}))
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaBinarySensorEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))
    async_add_entities(devs)


class MideaDeviceStatusSensorEntity(MideaEntity, BinarySensorEntity):
    """Device status binary sensor."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        super().__init__(
            coordinator,
            device.device_id,
            device.device_name,
            f"T0x{device.device_type:02X}",
            device.sn,
            device.sn8,
            device.model,
            entity_key
        )
        self._device = device
        self._manufacturer = manufacturer
        self._rationale = rationale
        self._config = config

    @property
    def entity_id_suffix(self) -> str:
        """Return the suffix for entity ID."""
        return "status"

    @property
    def device_class(self):
        """Return the device class."""
        return BinarySensorDeviceClass.CONNECTIVITY

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:devices"

    @property
    def is_on(self):
        """Return if the device is connected."""
        return self.coordinator.data.connected

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        return self.device_attributes


class MideaBinarySensorEntity(MideaEntity, BinarySensorEntity):
    """Generic binary sensor entity."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        super().__init__(
            coordinator,
            device.device_id,
            device.device_name,
            f"T0x{device.device_type:02X}",
            device.sn,
            device.sn8,
            device.model,
            entity_key
        )
        self._device = device
        self._manufacturer = manufacturer
        self._rationale = rationale
        self._entity_key = entity_key
        self._config = config

    @property
    def entity_id_suffix(self) -> str:
        """Return the suffix for entity ID."""
        return f"binary_sensor_{self._entity_key}"

    @property
    def is_on(self):
        """Return if the binary sensor is on."""
        value = self.device_attributes.get(self._entity_key)
        if isinstance(value, bool):
            return value
        return value == 1 or value == "on" or value == "true"
