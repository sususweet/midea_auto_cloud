"""Offline mapping/control tests; optional real codec checks use GR6_LUA_PATH."""

import asyncio
from copy import deepcopy
import os
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError

from custom_components.midea_auto_cloud import get_device_mapping
from custom_components.midea_auto_cloud.button import MideaButtonEntity
from custom_components.midea_auto_cloud.core.device import MiedaDevice
from custom_components.midea_auto_cloud.data_coordinator import (
    MideaDataUpdateCoordinator,
)
from custom_components.midea_auto_cloud.device_mapping.T0xBF import DEVICE_MAPPING
from custom_components.midea_auto_cloud.number import MideaNumberEntity
from custom_components.midea_auto_cloud.select import MideaSelectEntity


def coordinator():
    config = deepcopy(DEVICE_MAPPING["700006DJ"])
    firmware = {
        "work_status": "standby",
        "work_mode": "ff",
        "door_open": "off",
        "lock": "off",
        "error_code": 0,
        "execute": "ok",
    }
    device = SimpleNamespace(
        device_type=0xBF,
        subtype="5",
        device_name="Test appliance",
        connected=True,
        _ip_address=None,
        attributes={
            **firmware,
            "gr6_microwave_seconds": None,
            "gr6_microwave_power": None,
        },
        _skipped_queries=set(),
        _calculate_set=config["calculate"]["set"],
        _default_values={
            key: entity["default_value"]
            for platform in (Platform.NUMBER, Platform.SELECT)
            for key, entity in config["entities"][platform].items()
        },
        _coerce_calc_val=MiedaDevice._coerce_calc_val,
    )

    async def refresh():
        device.attributes.update(firmware)
        return True

    async def send(command):
        firmware.update(command)
        if "work_mode" in command:
            firmware["work_status"] = "work"
        return True

    device.refresh_status = AsyncMock(side_effect=refresh)
    device.set_attributes = AsyncMock(side_effect=send)
    c = object.__new__(MideaDataUpdateCoordinator)
    c.device = device
    c._device_id = 1
    c._cloud = None
    c._consecutive_poll_failures = 0
    c._control_lock = asyncio.Lock()
    c.mute_state_update_for_a_while = Mock()

    def publish(data):
        c.data = data

    c.async_set_updated_data = Mock(side_effect=publish)
    c.data = c._snapshot()
    c.firmware = firmware
    c.mapping = config
    return c


def entity(c, platform, key):
    cls = {
        Platform.BUTTON: MideaButtonEntity,
        Platform.NUMBER: MideaNumberEntity,
        Platform.SELECT: MideaSelectEntity,
    }[platform]
    result = object.__new__(cls)
    result.coordinator = c
    result._config = deepcopy(c.mapping["entities"][platform][key])
    result._entity_key = key
    result._device = c.device
    if platform == Platform.NUMBER:
        result._min_value = result._config["min"]
        result._max_value = result._config["max"]
        result._step = result._config["step"]
    elif platform == Platform.SELECT:
        result._key_options = result._config["options"]
        result._include_current = []
        result._ignore_values = []
        result._status_key = None
        result._last_option = None
    return result


async def stage(c, seconds=30, power="medium"):
    await entity(
        c, Platform.NUMBER, "gr6_microwave_seconds"
    ).async_set_native_value(seconds)
    await entity(
        c, Platform.SELECT, "gr6_microwave_power"
    ).async_select_option(power)


async def press(c, action):
    await entity(c, Platform.BUTTON, f"gr6_{action}").async_press()


class ControlsTest(unittest.IsolatedAsyncioTestCase):
    async def test_real_number_and_select_stage_without_sending_or_polling(self):
        c = coordinator()
        await stage(c, 65, "medium_low")
        c.device.set_attributes.assert_not_awaited()
        c.device.refresh_status.assert_not_awaited()
        self.assertEqual(c.data.attributes["gr6_microwave_seconds"], "65")
        self.assertEqual(c.data.attributes["gr6_microwave_power"], "fire_power_3")
        self.assertEqual(c.data.attributes["work_status"], "standby")

    async def test_start_uses_existing_calculations_for_duration_and_all_powers(self):
        for seconds in (5, 65, 1795):
            for power, code in (
                ("low", 1), ("medium_low", 3), ("medium", 5),
                ("medium_high", 8), ("high", 10),
            ):
                with self.subTest(seconds=seconds, power=power):
                    c = coordinator()
                    await stage(c, seconds, power)
                    await press(c, "start_microwave")
                    c.device.set_attributes.assert_awaited_once_with({
                        "work_mode": "microwave_1",
                        "work_hour": 0,
                        "pre_heat": "off",
                        "work_second": seconds % 60,
                        "fire_power": f"fire_power_{code}",
                        "work_minute": seconds // 60,
                    })
                    self.assertEqual(c.data.attributes["work_status"], "work")
                    self.assertEqual(
                        c.data.attributes["gr6_microwave_seconds"], str(seconds)
                    )

    async def test_missing_or_invalid_drafts_never_send(self):
        for key, value in (
            ("gr6_microwave_seconds", None),
            ("gr6_microwave_seconds", True),
            ("gr6_microwave_seconds", 0),
            ("gr6_microwave_seconds", 6),
            ("gr6_microwave_seconds", 1800),
            ("gr6_microwave_seconds", float("nan")),
            ("gr6_microwave_power", None),
            ("gr6_microwave_power", "unknown"),
        ):
            with self.subTest(key=key, value=value):
                c = coordinator()
                await stage(c)
                c.device.attributes[key] = value
                c.data = c._snapshot()
                with self.assertRaises(HomeAssistantError):
                    await press(c, "start_microwave")
                c.device.set_attributes.assert_not_awaited()

    async def test_reused_button_reads_new_drafts_without_mutating_its_template(self):
        c = coordinator()
        button = entity(c, Platform.BUTTON, "gr6_start_microwave")
        original = deepcopy(button._config["command"])
        await stage(c)
        await button.async_press()
        await press(c, "cancel")
        await stage(c, 65, "high")
        await button.async_press()
        command = c.device.set_attributes.await_args.args[0]
        self.assertEqual(command["work_minute"], 1)
        self.assertEqual(command["work_second"], 5)
        self.assertEqual(command["fire_power"], "fire_power_10")
        self.assertEqual(button._config["command"], original)

    async def test_start_and_resume_check_fresh_door_lock_fault_and_work_state(self):
        for action, before, wrong in (
            ("start_microwave", "standby", "work"),
            ("resume", "pause", "standby"),
        ):
            for key, value in (
                ("door_open", "on"), ("door_open", None),
                ("lock", "on"), ("lock", None),
                ("error_code", 1), ("error_code", None),
                ("work_status", wrong),
            ):
                with self.subTest(action=action, key=key, value=value):
                    c = coordinator()
                    await stage(c)
                    c.firmware.update(work_status=before)
                    c.firmware[key] = value
                    with self.assertRaises(HomeAssistantError):
                        await press(c, action)
                    c.device.set_attributes.assert_not_awaited()

    async def test_missing_fresh_field_cannot_reuse_old_safe_state(self):
        c = coordinator()
        await stage(c)
        del c.firmware["door_open"]
        with self.assertRaises(HomeAssistantError):
            await press(c, "start_microwave")
        c.device.set_attributes.assert_not_awaited()

    async def test_failed_or_skipped_queries_block_control(self):
        for kind in ("failed", "already_skipped", "newly_skipped"):
            with self.subTest(kind=kind):
                c = coordinator()
                await stage(c)
                if kind == "already_skipped":
                    c.device._skipped_queries.add(())
                else:
                    async def refresh():
                        c.device.attributes.update(c.firmware)
                        if kind == "newly_skipped":
                            c.device._skipped_queries.add(())
                        return kind != "failed"

                    c.device.refresh_status.side_effect = refresh
                with self.assertRaises(HomeAssistantError):
                    await press(c, "start_microwave")
                c.device.set_attributes.assert_not_awaited()
                self.assertFalse(c.data.available)

    async def test_pause_resume_cancel_only_send_work_status(self):
        for action, before, after in (
            ("pause", "work", "pause"),
            ("resume", "pause", "work"),
            ("cancel", "work", "standby"),
        ):
            with self.subTest(action=action):
                c = coordinator()
                c.firmware["work_status"] = before
                if action == "cancel":
                    c.firmware["door_open"] = "on"
                await press(c, action)
                c.device.set_attributes.assert_awaited_once_with(
                    {"work_status": after}
                )
                self.assertEqual(c.data.attributes["work_status"], after)

    async def test_rejection_omitted_execute_or_unchanged_state_never_retries(self):
        for kind in ("transport", "rejection", "missing_execute", "unchanged"):
            with self.subTest(kind=kind):
                c = coordinator()
                await stage(c)

                async def send(command):
                    if kind != "unchanged":
                        c.firmware.update(command, work_status="work")
                    if kind == "rejection":
                        c.firmware["execute"] = "remote_control_closed"
                    elif kind == "missing_execute":
                        del c.firmware["execute"]
                    return kind != "transport"

                c.device.set_attributes.side_effect = send
                with patch(
                    "custom_components.midea_auto_cloud.data_coordinator.asyncio.sleep",
                    new=AsyncMock(),
                ):
                    with self.assertRaises(HomeAssistantError):
                        await press(c, "start_microwave")
                c.device.set_attributes.assert_awaited_once()
                if kind == "unchanged":
                    self.assertEqual(
                        c.data.attributes["work_status"], "standby"
                    )

    async def test_new_execution_result_replaces_cached_error(self):
        c = coordinator()
        await stage(c)
        c.firmware["execute"] = "door_open"

        async def send(command):
            c.firmware.update(command, work_status="work", execute="ok")
            return True

        c.device.set_attributes.side_effect = send
        await press(c, "start_microwave")
        self.assertEqual(c.data.attributes["execute"], "ok")

    async def test_unverified_subtype_never_sends_or_refreshes(self):
        c = coordinator()
        await stage(c)
        c.device.subtype = "other"
        with self.assertRaises(HomeAssistantError):
            await press(c, "start_microwave")
        c.device.refresh_status.assert_not_awaited()
        c.device.set_attributes.assert_not_awaited()

    async def test_concurrent_start_presses_do_not_send_two_heating_commands(self):
        c = coordinator()
        await stage(c)
        results = await asyncio.gather(
            press(c, "start_microwave"),
            press(c, "start_microwave"),
            return_exceptions=True,
        )
        self.assertEqual(sum(r is None for r in results), 1)
        self.assertEqual(
            sum(isinstance(r, HomeAssistantError) for r in results), 1
        )
        c.device.set_attributes.assert_awaited_once()

    async def test_generic_control_is_not_tied_to_microwave_fields_or_model(self):
        c = coordinator()
        c.device.subtype = "unrelated"
        c.firmware["power"] = "off"
        await c.async_execute_control(
            {"power": "on"},
            {"require": {"power": ["off"]}, "confirm": {"power": ["on"]}},
        )
        c.device.set_attributes.assert_awaited_once_with({"power": "on"})
        self.assertEqual(c.data.attributes["power"], "on")

    async def test_unconfigured_button_retains_optimistic_command_path(self):
        c = coordinator()
        button = entity(c, Platform.BUTTON, "gr6_pause")
        button._config = {"command": {"power": "on"}}
        await button.async_press()
        c.device.set_attributes.assert_awaited_once_with({"power": "on"})
        c.device.refresh_status.assert_not_awaited()
        c.mute_state_update_for_a_while.assert_called_once()
        self.assertEqual(c.data.attributes["power"], "on")

    async def test_include_current_list_preserves_explicit_command_values(self):
        c = coordinator()
        button = entity(c, Platform.BUTTON, "gr6_pause")
        button._config = {
            "command": {"work_status": "pause"},
            "include_current": ["work_status", "lock"],
        }
        await button.async_press()
        c.device.set_attributes.assert_awaited_once_with({
            "work_status": "pause", "lock": "off",
        })


class MappingAndProtocolTest(unittest.IsolatedAsyncioTestCase):
    def test_only_verified_sn8_has_controls_and_default_sensors_are_preserved(self):
        other = get_device_mapping(DEVICE_MAPPING, 0xBF, "other", subtype="5")
        verified = get_device_mapping(
            DEVICE_MAPPING, 0xBF, "700006DJ", subtype="5"
        )
        self.assertNotIn(Platform.BUTTON, other["entities"])
        self.assertEqual(
            verified["entities"][Platform.SENSOR],
            other["entities"][Platform.SENSOR],
        )
        self.assertEqual(verified["centralized"], [])

    @unittest.skipUnless(
        os.environ.get("GR6_LUA_PATH"), "Set GR6_LUA_PATH for real codec checks"
    )
    async def test_actual_lua_encodes_commands_emitted_by_mapping_pipeline(self):
        from custom_components.midea_auto_cloud.core.lua_runtime import MideaCodec

        codec = MideaCodec(
            os.environ["GR6_LUA_PATH"], device_type="T0xBF", subtype="5"
        )
        context = {"work_mode": "microwave_1", "work_status": "work"}
        for seconds in (5, 65, 1795):
            c = coordinator()
            await stage(c, seconds, "medium_low")
            await press(c, "start_microwave")
            command = c.device.set_attributes.await_args.args[0]
            frame = bytes.fromhex(codec.build_control(command, status=context))
            self.assertEqual(frame[9:11], bytes([2, 1]))
            self.assertEqual(
                frame[16:22],
                bytes([1, 1, 0, seconds // 60, seconds % 60, 3]),
            )
        for action, before, code in (
            ("pause", "work", 6),
            ("resume", "pause", 3),
            ("cancel", "work", 2),
        ):
            c = coordinator()
            c.firmware["work_status"] = before
            await press(c, action)
            command = c.device.set_attributes.await_args.args[0]
            frame = bytes.fromhex(codec.build_control(command, status=context))
            self.assertEqual(frame[9:12], bytes([2, 2, code]))
            self.assertEqual(len(frame), 19)


if __name__ == "__main__":
    unittest.main()
