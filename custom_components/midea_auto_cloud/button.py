"""Button entities for Midea Auto Cloud integration."""

import asyncio

from homeassistant.components.button import ButtonEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities for Midea devices."""
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.BUTTON,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaButtonEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaButtonEntity(MideaEntity, ButtonEntity):
    """Midea button entity."""

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

    async def async_press(self) -> None:
        """Press the button."""
        command_builder = self._config.get("command_builder")

        # For start_wash: auto power-on if the device is off before running
        # validators (which would otherwise reject the operation).
        if command_builder == "start_wash":
            from .device_mapping.T0xE1 import get_status_num
            data = self.device_attributes
            keep_start_now = getattr(self.coordinator, "_keep_start_now", False)
            status_num = get_status_num(
                data.get("work_status"),
                airswitch=data.get("airswitch", 0),
                air_left_hour=data.get("air_left_hour", 0),
                dryswitch=data.get("dryswitch", 0),
                keep_start_now=keep_start_now,
            )
            if status_num == 0:
                await self.coordinator.async_set_control({"work_status": "power_on"})
                # Poll for power-on readiness (matching smart_home logic).
                # Device may report power_on / standby / cancel as its
                # powered-up work_status — any status_num != 0 means ready.
                for _ in range(100):  # max 10s
                    await asyncio.sleep(0.1)
                    ws = self.device_attributes.get("work_status", "")
                    if get_status_num(ws) != 0:
                        break
                else:
                    raise HomeAssistantError("设备开机超时，请检查设备")

        await self._run_validators()

        if command_builder:
            command = await self._build_with_hook(command_builder)
        else:
            command = dict(self._config.get("command", {}))

        if command:
            # ── Clear local_only cache BEFORE sending command ──
            # The command dict is already fully built by _build_with_hook,
            # so _local_data values are no longer needed.  Clearing first
            # avoids a race: async_set_control yields the event loop, and
            # a device status callback could fire mid-await, seed mode,
            # then get deleted by _clear_local_data running afterwards.
            if command_builder in ("start_wash", "order"):
                self._clear_local_data()
            action = command.pop("_action", None)
            if action == "cancel_keep_then_start":
                await self.coordinator.async_set_control({"airswitch": 0})
                await self.coordinator.async_set_control({"airswitch": 2})
            else:
                await self.coordinator.async_set_control(command)
        elif command_builder:
            MideaLogger.info(
                "Button %s (%s): device not in operable state, no command sent"
                % (self._entity_key, command_builder),
            )

    async def _run_validators(self) -> None:
        """Run all configured validators."""
        validators = self._validators
        if not validators:
            return
        from .device_mapping.T0xE1 import dispatch_validator
        data = self.device_attributes
        diff_flags = getattr(self.coordinator, "_diff_flags", {}) or {}
        keep_start_now = getattr(self.coordinator, "_keep_start_now", False)
        for v in validators:
            await dispatch_validator(v, data, diff_flags, keep_start_now)

    async def _build_with_hook(self, builder_name: str) -> dict:
        """Call E1 command builder (device_attributes already merges _local_data)."""
        from .device_mapping.T0xE1 import (
            get_status_num, build_start_command, build_cancel_command,
            build_pause_command, build_order_command, calc_condition_result,
        )

        data = self.device_attributes
        diff_flags = getattr(self.coordinator, "_diff_flags", {}) or {}
        keep_start_now = getattr(self.coordinator, "_keep_start_now", False)
        status_num = get_status_num(
            data.get("work_status"),
            airswitch=data.get("airswitch", 0),
            air_left_hour=data.get("air_left_hour", 0),
            dryswitch=data.get("dryswitch", 0),
            keep_start_now=keep_start_now,
        )
        mapping = getattr(self.coordinator, "_device_mapping", {}) or {}
        mode_conditions = mapping.get("_mode_conditions", {})
        bright_condition = mapping.get("_bright_condition", False)
        mode_features = getattr(self.coordinator, "_mode_features", {}) or {}

        # Log condition matching for start/order
        if builder_name in ("start_wash", "order") and mode_conditions:
            mode_name = data.get("mode", "")
            if mode_name and mode_name in mode_conditions:
                result = calc_condition_result(
                    mode_name, mode_conditions, data, bright_condition
                )
                if result:
                    MideaLogger.debug(
                        f"Condition match mode={mode_name} "
                        f"bright_lack={data.get('bright_lack')} → {result}"
                    )

        if builder_name == "start_wash":
            return build_start_command(
                data, status_num, diff_flags, mode_features,
                last_user_mode=self.coordinator.last_user_mode,
            )

        if builder_name == "cancel":
            return build_cancel_command(status_num)

        if builder_name == "pause":
            return build_pause_command(data, status_num)

        if builder_name == "order":
            return build_order_command(
                data, diff_flags, mode_features,
                last_user_mode=self.coordinator.last_user_mode,
            )

        return {}

    def _clear_local_data(self) -> None:
        """Clear SELECT's local_only cache after command is sent.

        Preserve order_target_hour / order_target_min so the TIME entity
        (order_set_time) keeps its user-set values for subsequent orders.

        After clearing, immediately re-seed the mode from last_user_mode
        (matching smart_home's auto-seed in _on_device_update).  Without
        this, the wash_mode SELECT shows blank until the next device push.
        """
        try:
            local = self.coordinator.device._local_data
            if local:
                preserved = {}
                for k in ("order_target_hour", "order_target_min"):
                    if k in local:
                        preserved[k] = local[k]
                local.clear()
                local.update(preserved)
                # ── Immediate re-seed: restore mode from last_user_mode ──
                # Without this, the SELECT's current_option shows blank
                # (device reports neutral_gear / "" / invalid in idle).
                self.coordinator._auto_seed_e1_mode()
        except Exception:
            pass
