from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.LOCK,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaLockEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaLockEntity(MideaEntity, LockEntity):
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
        self._command = config.get("command")
        self._include_current = config.get("include_current") or []

    @property
    def is_locked(self) -> bool:
        attribute = self._config.get("attribute", self._entity_key)
        return self._get_status_on_off(attribute)

    async def _async_set_status_locked(self, locked: bool) -> None:
        attribute = self._config.get("attribute", self._entity_key)
        if attribute is None:
            return
        value = self._on_off_wire_value(locked, attribute)
        merged_command = {}
        if isinstance(self._command, dict):
            merged_command.update(self._command)
        merged_command[attribute] = value

        for attr in self._include_current:
            current_value = self._get_nested_value(attr)
            if current_value is not None:
                merged_command[attr] = current_value

        await self.async_set_attributes(merged_command)

    async def async_lock(self, **kwargs: Any) -> None:
        await self._async_set_status_locked(True)

    async def async_unlock(self, **kwargs: Any) -> None:
        await self._async_set_status_locked(False)
