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
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        try:
                            if float(state_value) != float(value):
                                match = False
                                break
                            continue
                        except (TypeError, ValueError):
                            match = False
                            break
                    if isinstance(value, str):
                        if str(state_value) == value:
                            continue
                        try:
                            if float(state_value) == float(value):
                                continue
                        except (TypeError, ValueError):
                            pass
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
            # No match and not ignored: device reports an internal state
            # (e.g. neutral_gear / "" / invalid in idle) that is not in
            # the option list.  Show the last user-selected mode so the
            # UI never flashes blank (matching smart_home behaviour).
            if self._last_option is not None:
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

        # Run validators
        await self._run_validators(option)

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

        if self._local_only:
            # ── Clear stale sub-feature values when wash mode changes ──
            local_data = self.coordinator.device._local_data
            if self._entity_key == "wash_mode":
                for key in list(local_data):
                    if key != "mode":
                        del local_data[key]
                # Store the actual mode identifier (e.g. "glass_wash"),
                # not the display key (e.g. "轻柔洗").  This is needed
                # by _auto_seed_e1_mode and build_start_command.
                actual_mode = merged_command.get("mode", option)
                self.coordinator.last_user_mode = actual_mode

            local_data.update(merged_command)
            # ── Optimistic UI update: notify coordinator so ALL mode_dependent
            #     entities immediately re-check their available property.
            self.async_write_ha_state()
            self.coordinator.async_update_listeners()
        elif merged_command:
            await self.async_set_attributes(merged_command)
        else:
            await self.async_set_attributes(new_status)

    async def _run_validators(self, option: str) -> None:
        if not self._validators:
            return
        from .device_mapping.T0xE1 import dispatch_validator
        data = self.device_attributes
        diff_flags = getattr(self.coordinator, "_diff_flags", {}) or {}
        keep_start_now = getattr(self.coordinator, "_keep_start_now", False)
        for v in self._validators:
            await dispatch_validator(
                v, data, diff_flags, keep_start_now,
                option=option, options_map=self._key_options,
            )
