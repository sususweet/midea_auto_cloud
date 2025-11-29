"""Base entity class for Midea Auto Cloud integration."""

from __future__ import annotations

import logging
from enum import IntEnum
from typing import Any

from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .core.logger import MideaLogger
from .data_coordinator import MideaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class Rationale(IntEnum):
    EQUALLY = 0
    GREATER = 1
    LESS = 2

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
        entity_key: str,
        *,
        device: Any | None = None,
        manufacturer: str | None = None,
        rationale: list | None = None,
        config: dict | None = None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._device_type = device_type
        self._entity_key = entity_key
        self._sn = sn
        self._sn8 = sn8
        self._model = model
        # Legacy/extended fields
        self._device = device
        self._config = config or {}
        self._rationale = rationale
        if (self._config.get("rationale")) is not None:
            self._rationale = self._config.get("rationale")
        if self._rationale is None:
            self._rationale = ["off", "on"]
        
        # Display and identification
        self._attr_has_entity_name = True
        # Prefer legacy unique_id scheme if device object is available (device_id based)
        if self._device is not None:
            self._attr_unique_id = f"{DOMAIN}.{self._device_id}_{self._entity_key}"
            self.entity_id_base = f"midea_{self._device_id}"
            manu = "Midea" if manufacturer is None else manufacturer
            self.manufacturer = manu
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, str(self._device_id))},
                model=self._model,
                serial_number=sn,
                manufacturer=manu,
                name=device_name,
            )
            # Presentation attributes from config
            self._attr_native_unit_of_measurement = self._config.get("unit_of_measurement")
            self._attr_device_class = self._config.get("device_class")
            self._attr_state_class = self._config.get("state_class")
            self._attr_icon = self._config.get("icon")
            # Prefer translated name; allow explicit override via config.name
            self._attr_translation_key = self._config.get("translation_key") or self._entity_key
            name_cfg = self._config.get("name")
            if name_cfg is not None:
                self._attr_name = f"{name_cfg}"
            self.entity_id = self._attr_unique_id
            # Register device updates for HA state refresh
            try:
                self._device.register_update(self.update_state)  # type: ignore[attr-defined]
            except Exception:
                pass
        else:
            # Fallback to sn8-based unique id/device info
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
        return self.coordinator.data.attributes if self.coordinator.data else {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self.coordinator.data:
            return self.coordinator.data.available
        else:
            return False

    async def _publish_command(self) -> None:
        """Publish commands to the device."""
        # This will be implemented by subclasses
        pass

    # ===== Unified helpers migrated from legacy entity base =====
    def _get_nested_value(self, attribute_key: str | None) -> Any:
        """Get nested value from device attributes using dot notation.
        
        Supports both flat and nested attribute access.
        Examples: 'power', 'eco.status', 'temperature.room'
        """
        if attribute_key is None:
            return None
        
        # Handle nested attributes with dot notation
        if '.' in attribute_key:
            keys = attribute_key.split('.')
            value = self.device_attributes
            try:
                for key in keys:
                    if isinstance(value, dict):
                        value = value.get(key)
                    else:
                        return None
                return value
            except (KeyError, TypeError):
                return None
        else:
            # Handle flat attributes
            return self.device_attributes.get(attribute_key)

    def _get_status_on_off(self, attribute_key: str | None) -> bool:
        """Return boolean value from device attributes for given key.

        Accepts common truthy representations: True/1/"on"/"true".
        Supports nested attributes with dot notation.
        """
        result = False
        if attribute_key is None:
            return result
        status = self._get_nested_value(attribute_key)
        if status is not None:
            try:
                result = bool(self._rationale.index(status))
            except ValueError:
                if int(status) == 0:
                    result = False
                else:
                    result = True
                MideaLogger.info(f"The value of attribute {attribute_key} ('{status}') "
                                  f"is not in rationale {self._rationale}")
                return result
        return result

    def _set_nested_value(self, attribute_key: str, value: Any) -> None:
        """Set nested value in device attributes using dot notation.
        
        Supports both flat and nested attribute setting.
        Examples: 'power', 'eco.status', 'temperature.room'
        """
        if attribute_key is None:
            return
        
        # Handle nested attributes with dot notation
        if '.' in attribute_key:
            keys = attribute_key.split('.')
            current_dict = self.device_attributes
            
            # Navigate to the parent dictionary
            for key in keys[:-1]:
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]
            
            # Set the final value
            current_dict[keys[-1]] = value
        else:
            # Handle flat attributes
            self.device_attributes[attribute_key] = value

    async def _async_set_status_on_off(self, attribute_key: str | None, turn_on: bool) -> None:
        """Set boolean attribute via coordinator, no-op if key is None."""
        if attribute_key is None:
            return
        await self.async_set_attribute(attribute_key, self._rationale[int(turn_on)])

    def _list_get_selected(self, key_of_list: list, rationale: Rationale = Rationale.EQUALLY):
        for index in range(0, len(key_of_list)):
            match = True
            for attr, value in key_of_list[index].items():
                state_value = self._get_nested_value(attr)
                if state_value is None:
                    match = False
                    break
                if rationale is Rationale.EQUALLY and state_value != value:
                    match = False
                    break
                if rationale is Rationale.GREATER and state_value < value:
                    match = False
                    break
                if rationale is Rationale.LESS and state_value > value:
                    match = False
                    break
            if match:
                return index
        return None

    def _dict_get_selected(self, key_of_dict: dict, rationale: Rationale = Rationale.EQUALLY):
        for mode, status in key_of_dict.items():
            match = True
            for attr, value in status.items():
                state_value = self._get_nested_value(attr)
                if state_value is None:
                    match = False
                    break
                if rationale is Rationale.EQUALLY and state_value != value:
                    match = False
                    break
                if rationale is Rationale.GREATER and state_value < value:
                    match = False
                    break
                if rationale is Rationale.LESS and state_value > value:
                    match = False
                    break
            if match:
                return mode
        return None

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
