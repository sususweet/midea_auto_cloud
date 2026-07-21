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

_YES_NO_VALUES = frozenset({"yes", "no"})


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
        self._condition = self._config.get("condition")
        self._name_cfg = None
        self._name_attribute = None
        # E1-specific features
        self._validators = self._config.get("validator", [])
        if isinstance(self._validators, str):
            self._validators = [self._validators]
        self._local_only = self._config.get("local_only", False)
        self._mode_dependent = self._config.get("mode_dependent", False)
        self._computed_status = self._config.get("computed_status", False)
        self._side_effect = self._config.get("side_effect")
        self._cloud_name = self._config.get("cloud_name")
        if self._cloud_name:
            self._attr_name = self._cloud_name
        if (self._config.get("rationale")) is not None:
            self._rationale = self._config.get("rationale")
        if self._rationale is None:
            self._rationale = ["off", "on"]
        
        # Display and identification
        self._attr_has_entity_name = True
        # Prefer legacy unique_id scheme if device object is available (device_id based)
        if self._device is not None:
            self._attr_unique_id = f"{DOMAIN}.{self._device_id}_{self._entity_key}".lower()
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

            # 保存固定名称配置
            self._name_cfg = self._config.get("name")
            # 保存 name_attribute，用于动态获取名称
            self._name_attribute = self._config.get("name_attribute")
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
    def name(self) -> str | None:
        """Return the name of the entity.

        动态从设备属性获取名称，支持云端名称更新后自动同步。
        优先使用自定义配置的名称，如果没有则回退到基类逻辑。
        """
        # 如果配置了固定的 name，直接使用
        if self._name_cfg is not None:
            return f"{self._name_cfg}"
        # 如果配置了 name_attribute，从设备属性动态获取
        if self._name_attribute and self._device:
            dynamic_name = self._device._attributes.get(self._name_attribute)
            if dynamic_name:
                return dynamic_name
        # 如果没有自定义名称，调用基类的 name 属性
        return super().name

    @property
    def device_attributes(self) -> dict:
        """Return device attributes."""
        attrs = self.coordinator.data.attributes if self.coordinator.data else {}
        ld = self.coordinator.device._local_data
        if ld:
            attrs = dict(attrs)
            attrs.update(ld)
        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.data or not self.coordinator.data.available:
            return False
        # Device-level filtering: entity key in _missing_features means
        # this device does not support the feature at all (per cloud config).
        # This replaces init-time .pop() — DEVICE_MAPPING stays intact.
        missing = getattr(self.coordinator, "_missing_features", None)
        if missing and self._entity_key in missing:
            return False
        # mode_dependent: read user-selected mode from local cache instead of
        # device-reported mode (which may be neutral_gear / "" / invalid in
        # idle state).  Without a selected mode, hide all mode-dependent
        # entities (temperature, region, additional, etc.).
        if self._mode_dependent:
            local_mode = self.coordinator.device._local_data.get("mode", "")
            if not local_mode:
                local_mode = getattr(self.coordinator, "last_user_mode", "")
            if not local_mode:
                return False
            mode_features = getattr(self.coordinator, "_mode_features", {}) or {}
            if mode_features:
                if self._entity_key not in mode_features.get(local_mode, set()):
                    return False
        return self._check_condition(self._condition)

    def _check_condition(self, condition: dict | None = None) -> bool:
        condition = condition or self._condition
        if not condition:
            return True

        if "not" in condition:
            for attr in condition["not"]:
                if self.device_attributes.get(attr):
                    return False
            return True

        if "eq" in condition:
            attr, expected_value = condition["eq"]
            return self.device_attributes.get(attr) == expected_value

        return True

    def _extract_deepest_value(self, config: dict) -> Any:
        for value in config.values():
            if isinstance(value, dict):
                return self._extract_deepest_value(value)
            return value
        return None

    async def _publish_command(self) -> None:
        """Publish commands to the device."""
        # This will be implemented by subclasses
        pass

    # ===== Unified helpers migrated from legacy entity base =====
    def _get_nested_value(self, attribute_key: str | None) -> Any:
        """Get value from device attributes.

        Resolution order for dotted keys:
        1. Exact flat key with a real value (literal ``mode.current``)
        2. Nested path (``mode`` → ``current``)
        3. Underscore flat key (``mode_current``)
        4. Exact flat key even if None (preset placeholders)

        Mapping setup may preset dotted keys to None (e.g. ``temperature.room``).
        Those must not shadow a live nested payload under ``temperature.room``.
        """
        if attribute_key is None:
            return None

        attrs = self.device_attributes
        if not isinstance(attrs, dict):
            return None

        if attribute_key in attrs:
            exact = attrs[attribute_key]
            # Non-None exact wins (flat #216-style literal dotted keys).
            # None may be only a mapping preset — keep looking.
            if exact is not None or "." not in attribute_key:
                return exact

        if "." not in attribute_key:
            return None

        value: Any = attrs
        for key in attribute_key.split("."):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                underscore = attrs.get(attribute_key.replace(".", "_"))
                if underscore is not None:
                    return underscore
                # Fall back to preset exact key (None) if nothing else matched
                return attrs.get(attribute_key)
        return value

    def _coerce_on_off(self, value: Any) -> bool | None:
        """Normalize common on/off wire formats to bool."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)) and int(value) in (0, 1):
            return bool(int(value))
        if isinstance(value, str):
            normalized = value.lower()
            if normalized in ("yes", "on", "true", "1"):
                return True
            if normalized in ("no", "off", "false", "0"):
                return False
        return None

    def _on_off_wire_value(self, turn_on: bool, attribute_key: str | None = None) -> Any:
        """Return the on/off value to send, matching the device's wire format."""
        if attribute_key:
            current = self._get_nested_value(attribute_key)
            if isinstance(current, str) and current.lower() in _YES_NO_VALUES:
                return "yes" if turn_on else "no"
        return self._rationale[int(turn_on)]

    def _get_status_on_off(self, attribute_key: str | None) -> bool:
        """Return boolean value from device attributes for given key.

        Accepts rationale values plus common aliases: yes/no, on/off, 0/1, true/false.
        Supports nested attributes with dot notation.
        Supports status_key config override (e.g. power switch reads "work_status").
        """
        if attribute_key is None:
            return False
        status_key = self._config.get("status_key", attribute_key)
        status = self._get_nested_value(status_key)
        if status is None:
            return False
        try:
            return bool(self._rationale.index(status))
        except ValueError:
            coerced = self._coerce_on_off(status)
            if coerced is not None:
                return coerced
            MideaLogger.warning(
                f"The value of attribute {attribute_key} ('{status}') "
                f"is not in rationale {self._rationale}"
            )
            return False

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
        await self.async_set_attribute(attribute_key, self._on_off_wire_value(turn_on, attribute_key))

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

    def _values_equal_soft(self, state_value: Any, expected: Any) -> bool:
        """Loose equality for wire formats (on/off aliases, numeric strings)."""
        if state_value == expected:
            return True
        state_on_off = self._coerce_on_off(state_value)
        expected_on_off = self._coerce_on_off(expected)
        if state_on_off is not None and expected_on_off is not None:
            return state_on_off == expected_on_off
        try:
            return float(state_value) == float(expected)
        except (TypeError, ValueError):
            return str(state_value) == str(expected)

    def _dict_get_selected(self, key_of_dict: dict, rationale: Rationale = Rationale.EQUALLY):
        for mode, status in key_of_dict.items():
            match = True
            for attr, value in status.items():
                state_value = self._get_nested_value(attr)
                if state_value is None:
                    match = False
                    break
                if rationale is Rationale.EQUALLY and not self._values_equal_soft(state_value, value):
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
