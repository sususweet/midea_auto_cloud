"""Run with unittest in a Home Assistant environment; no network calls.

Set GR6_LUA_PATH to an already downloaded device Lua file to additionally
exercise the real codec. The vendor file is intentionally not distributed.
"""

import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "midea_auto_cloud"
    / "gr6_pro.py"
)
spec = importlib.util.spec_from_file_location("gr6_pro_tested", SOURCE)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def coordinator():
    attributes = {
        adapter.SECONDS: "30",
        adapter.POWER: "fire_power_5",
        "work_status": "standby",
        "work_mode": "ff",
        "door_open": "off",
        "lock": "off",
        "error_code": 0,
        "execute": "ok",
    }
    device = SimpleNamespace(
        device_type=0xBF,
        sn8="700006DJ",
        subtype="5",
        attributes=attributes,
        _skipped_queries=set(),
        refresh_status=AsyncMock(return_value=True),
    )

    async def send(command):
        attributes.update(command)
        if "work_mode" in command:
            attributes["work_status"] = "work"
        return True

    device.set_attributes = AsyncMock(side_effect=send)
    return SimpleNamespace(
        device=device,
        _track_poll_result=Mock(),
        _snapshot=Mock(return_value=SimpleNamespace(attributes=attributes)),
        async_set_updated_data=Mock(),
    )


class ControlsTest(unittest.IsolatedAsyncioTestCase):
    async def test_start_sends_one_complete_microwave_command(self):
        c = coordinator()
        await adapter.async_execute(c, "start_microwave")
        c.device.set_attributes.assert_awaited_once_with({
            "work_mode": "microwave_1",
            "work_hour": 0,
            "work_minute": 0,
            "work_second": 30,
            "fire_power": "fire_power_5",
            "pre_heat": "off",
        })

    def test_duration_boundaries_and_medium_low_power(self):
        for value, minute, second in ((5, 0, 5), (65, 1, 5), (1795, 29, 55)):
            with self.subTest(seconds=value):
                command = adapter.microwave_command({
                    adapter.SECONDS: value,
                    adapter.POWER: "fire_power_3",
                })
                self.assertEqual(command["work_minute"], minute)
                self.assertEqual(command["work_second"], second)
                self.assertEqual(command["fire_power"], "fire_power_3")

    async def test_missing_invalid_or_out_of_range_settings_never_send(self):
        for value in (None, True, 0, 4, 6, 1800, float("nan")):
            with self.subTest(seconds=value):
                c = coordinator()
                c.device.attributes[adapter.SECONDS] = value
                with self.assertRaises(HomeAssistantError):
                    await adapter.async_execute(c, "start_microwave")
                c.device.set_attributes.assert_not_awaited()
        c = coordinator()
        c.device.attributes[adapter.POWER] = None
        with self.assertRaises(HomeAssistantError):
            await adapter.async_execute(c, "start_microwave")
        c.device.set_attributes.assert_not_awaited()

    async def test_fresh_door_lock_fault_and_running_states_block_start(self):
        for key, value in (
            ("door_open", "on"), ("door_open", None),
            ("lock", "on"), ("lock", None),
            ("error_code", 1), ("error_code", None),
            ("work_status", "work"), ("work_status", "pause"),
        ):
            with self.subTest(key=key, value=value):
                c = coordinator()

                async def refresh():
                    c.device.attributes[key] = value
                    return True

                c.device.refresh_status.side_effect = refresh
                with self.assertRaises(HomeAssistantError):
                    await adapter.async_execute(c, "start_microwave")
                c.device.set_attributes.assert_not_awaited()

    async def test_failed_or_skipped_refresh_blocks_control(self):
        for skipped in (False, True):
            c = coordinator()
            c.device.refresh_status.return_value = False
            if skipped:
                c.device._skipped_queries.add(())
            with self.assertRaises(HomeAssistantError):
                await adapter.async_execute(c, "start_microwave")
            c.device.set_attributes.assert_not_awaited()

    async def test_pause_resume_cancel_never_include_cooking_parameters(self):
        for action, before, after in (
            ("pause", "work", "pause"),
            ("resume", "pause", "work"),
            ("cancel", "work", "standby"),
        ):
            with self.subTest(action=action):
                c = coordinator()
                c.device.attributes["work_status"] = before
                if action == "cancel":
                    c.device.attributes["door_open"] = "on"
                await adapter.async_execute(c, action)
                c.device.set_attributes.assert_awaited_once_with(
                    {"work_status": after}
                )

    async def test_rejection_or_unconfirmed_state_is_not_success_or_retried(self):
        for kind in ("transport", "rejection", "unchanged"):
            with self.subTest(kind=kind):
                c = coordinator()
                c.device.set_attributes.side_effect = None
                c.device.set_attributes.return_value = kind != "transport"
                if kind == "rejection":
                    c.device.attributes["execute"] = "remote_control_closed"
                with patch.object(adapter.asyncio, "sleep", new=AsyncMock()):
                    with self.assertRaises(HomeAssistantError):
                        await adapter.async_execute(c, "start_microwave")
                c.device.set_attributes.assert_awaited_once()

    async def test_other_product_is_never_controlled(self):
        for key, value in (
            ("device_type", 0xB0), ("sn8", "other"), ("subtype", "other")
        ):
            with self.subTest(key=key):
                c = coordinator()
                setattr(c.device, key, value)
                with self.assertRaises(HomeAssistantError):
                    await adapter.async_execute(c, "start_microwave")
                c.device.refresh_status.assert_not_awaited()
                c.device.set_attributes.assert_not_awaited()

    async def test_staged_settings_use_existing_local_only_coordinator_path(self):
        from custom_components.midea_auto_cloud.data_coordinator import (
            MideaDataUpdateCoordinator,
        )

        c = coordinator()
        c.device._calculate_set = []
        c.device._default_values = {adapter.SECONDS: None, adapter.POWER: None}
        c.mute_state_update_for_a_while = Mock()
        settings = {adapter.SECONDS: "45", adapter.POWER: "fire_power_3"}
        await MideaDataUpdateCoordinator.async_set_attributes(c, settings)
        c.device.set_attributes.assert_not_awaited()
        for key, value in settings.items():
            self.assertEqual(c.device.attributes[key], value)


class ButtonTest(unittest.IsolatedAsyncioTestCase):
    async def test_gr6_button_dispatches_explicit_action(self):
        from custom_components.midea_auto_cloud.button import MideaButtonEntity

        entity = object.__new__(MideaButtonEntity)
        entity._config = {"gr6_pro_action": "pause"}
        entity.coordinator = coordinator()
        with patch(
            "custom_components.midea_auto_cloud.gr6_pro.async_execute",
            new_callable=AsyncMock,
        ) as execute:
            await entity.async_press()
            execute.assert_awaited_once_with(entity.coordinator, "pause")

    async def test_other_buttons_keep_existing_command_path(self):
        from custom_components.midea_auto_cloud.button import MideaButtonEntity

        entity = object.__new__(MideaButtonEntity)
        entity._config = {"command": {"power": "on"}}
        entity._entity_key = "ordinary_button"
        entity._device = None
        entity.async_set_attributes = AsyncMock()
        await entity.async_press()
        entity.async_set_attributes.assert_awaited_once_with({"power": "on"})


class MappingAndProtocolTest(unittest.TestCase):
    def test_existing_mapping_is_preserved_and_default_is_not_mutated(self):
        from custom_components.midea_auto_cloud.device_mapping.T0xBF import (
            DEVICE_MAPPING,
        )

        self.assertIn("700006DJ", DEVICE_MAPPING)
        original = {
            "entities": {Platform.SENSOR: {"work_status": {}}},
            "centralized": [],
        }
        mappings = {"default": original}
        adapter.add_gr6_pro_mapping(mappings)
        self.assertNotIn(Platform.BUTTON, original["entities"])
        self.assertEqual(
            mappings["700006DJ"]["entities"][Platform.SENSOR],
            original["entities"][Platform.SENSOR],
        )
        self.assertEqual(mappings["700006DJ"]["centralized"], [])

    @unittest.skipUnless(
        os.environ.get("GR6_LUA_PATH"), "Set GR6_LUA_PATH for real codec checks"
    )
    def test_actual_lua_encodes_microwave_and_status_commands_separately(self):
        from custom_components.midea_auto_cloud.core.lua_runtime import MideaCodec

        codec = MideaCodec(
            os.environ["GR6_LUA_PATH"], device_type="T0xBF", subtype="5"
        )
        for value in (5, 65, 1795):
            with self.subTest(seconds=value):
                command = adapter.microwave_command({
                    adapter.SECONDS: value,
                    adapter.POWER: "fire_power_3",
                })
                frame = bytes.fromhex(codec.build_control(command))
                self.assertEqual(frame[9:11], bytes([2, 1]))
                self.assertEqual(
                    frame[16:22],
                    bytes([1, 1, 0, value // 60, value % 60, 3]),
                )
        for state, code in (("pause", 6), ("work", 3), ("standby", 2)):
            frame = bytes.fromhex(codec.build_control({"work_status": state}))
            self.assertEqual(frame[9:12], bytes([2, 2, code]))
            self.assertEqual(len(frame), 19)


if __name__ == "__main__":
    unittest.main()
