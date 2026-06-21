from typing import Any

from homeassistant.components.select import SelectEntity
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
        Platform.SELECT,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaSelectEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaSelectEntity(MideaEntity, SelectEntity):
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
        self._key_options = self._config.get("options") or {}
        self._status_key = self._config.get("status_key")
        self._ignore_values = self._config.get("ignore_values") or []
        self._include_current = self._config.get("include_current") or []
        self._last_option: str | None = None

    @property
    def options(self):
        return list(self._key_options.keys())

    def _is_ignored_value(self, value: Any) -> bool:
        if value is None:
            return False
        for ignore_val in self._ignore_values:
            if value == ignore_val:
                return True
            try:
                if str(value) == str(ignore_val):
                    return True
            except (TypeError, ValueError):
                pass
        return False

    def _dict_get_selected_for_select(self) -> tuple[str | None, bool]:
        if not isinstance(self._key_options, dict):
            return None, False

        if self._status_key:
            current_value = self._get_nested_value(self._status_key)
            if current_value is not None:
                if self._is_ignored_value(current_value):
                    return None, True
                for mode, status in self._key_options.items():
                    extracted = self._extract_deepest_value(status)
                    if extracted == current_value:
                        return mode, False
            return None, False

        for mode, status in self._key_options.items():
            match = True
            for attr, value in status.items():
                state_value = self._get_nested_value(attr)
                if state_value is None:
                    match = False
                    break
                if self._is_ignored_value(state_value):
                    return None, True
                try:
                    if isinstance(value, int) and state_value != value:
                        match = False
                        break
                    if isinstance(value, str) and str(state_value) != value:
                        match = False
                        break
                except (TypeError, ValueError):
                    match = False
                    break
            if match:
                return mode, False
        return None, False

    @property
    def current_option(self):
        attribute = self._config.get("attribute", self._entity_key)
        if isinstance(self._key_options, dict):
            matched, ignored = self._dict_get_selected_for_select()
            if matched is not None:
                self._last_option = matched
                return matched
            if ignored:
                return self._last_option

        if attribute and attribute != self._entity_key:
            value = self._get_nested_value(attribute)
            if value is not None:
                if self._is_ignored_value(value):
                    return self._last_option
                if isinstance(value, str) and value in self.options:
                    self._last_option = value
                    return value
                try:
                    index = int(value)
                    if 0 <= index < len(self.options):
                        self._last_option = self.options[index]
                        return self.options[index]
                except (TypeError, ValueError):
                    pass
            return self._last_option

        return self._dict_get_selected(self._key_options)

    async def async_select_option(self, option: str):
        new_status = self._key_options.get(option)
        if not new_status:
            return

        self._last_option = option
        command = self._config.get("command")
        merged_command = {}
        if isinstance(new_status, dict):
            merged_command.update(new_status)
        if command and isinstance(command, dict):
            merged_command.update(command)
        for attr in self._include_current:
            if attr in merged_command:
                continue
            current_value = self._get_nested_value(attr)
            if current_value is not None:
                merged_command[attr] = current_value
        if merged_command:
            await self.async_set_attributes(merged_command)
        else:
            await self.async_set_attributes(new_status)
