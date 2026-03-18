from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass
)
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities for Midea devices."""
    def _per_device_hook(devs, coordinator, device, manufacturer, rationale, config):
        if coordinator and device:
            devs.append(MideaDeviceStatusSensorEntity(coordinator, device, manufacturer, rationale, "Status", {}))

    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.BINARY_SENSOR,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaBinarySensorEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
        per_device_hook=_per_device_hook,
    )


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
            entity_key,
            device=device,
            manufacturer=manufacturer,
            rationale=rationale,
            config=config,
        )
        self._device = device
        self._manufacturer = manufacturer
        self._rationale = rationale
        self._config = config

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
            entity_key,
            device=device,
            manufacturer=manufacturer,
            rationale=rationale,
            config=config,
        )
        self._device = device
        self._manufacturer = manufacturer
        self._rationale = rationale
        self._entity_key = entity_key
        self._config = config

    @property
    def is_on(self):
        """Return if the binary sensor is on."""
        value = self.device_attributes.get(self._entity_key)
        if isinstance(value, bool):
            return value
        return value == 1 or value == "on" or value == "true"
