"""Base entity class for Midea Auto Codec integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .data_coordinator import MideaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class MideaEntity(CoordinatorEntity[MideaDataUpdateCoordinator], Entity):
    """Base class for Midea entities."""

    def __init__(
        self,
        coordinator: MideaDataUpdateCoordinator,
        device_id: int,
        device_name: str,
        device_type: str,
        sn: str,
        sn8: str,
        model: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._device_type = device_type
        self._sn = sn
        self._sn8 = sn8
        self._model = model
        
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{sn8}_{self.entity_id_suffix}"
        self.entity_id_base = f"midea_{sn8.lower()}"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, sn8)},
            model=model,
            serial_number=sn,
            manufacturer="Midea",
            name=device_name,
        )
        
        # Debounced command publishing
        self._debounced_publish_command = Debouncer(
            hass=self.coordinator.hass,
            logger=_LOGGER,
            cooldown=2,
            immediate=True,
            background=True,
            function=self._publish_command,
        )
        
        if self.coordinator.config_entry:
            self.coordinator.config_entry.async_on_unload(
                self._debounced_publish_command.async_shutdown
            )

    @property
    def entity_id_suffix(self) -> str:
        """Return the suffix for entity ID."""
        return "base"

    @property
    def device_attributes(self) -> dict:
        """Return device attributes."""
        return self.coordinator.data.attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.available

    async def _publish_command(self) -> None:
        """Publish commands to the device."""
        # This will be implemented by subclasses
        pass

    async def publish_command_from_current_state(self) -> None:
        """Publish commands to the device from current state."""
        self.coordinator.mute_state_update_for_a_while()
        self.coordinator.async_update_listeners()
        await self._debounced_publish_command.async_call()

    async def async_set_attribute(self, attribute: str, value: Any) -> None:
        """Set a device attribute."""
        await self.coordinator.async_set_attribute(attribute, value)

    async def async_set_attributes(self, attributes: dict) -> None:
        """Set multiple device attributes."""
        await self.coordinator.async_set_attributes(attributes)

    async def async_send_command(self, cmd_type: int, cmd_body: str) -> None:
        """Send a command to the device."""
        await self.coordinator.async_send_command(cmd_type, cmd_body)
