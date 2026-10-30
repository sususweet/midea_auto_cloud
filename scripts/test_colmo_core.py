"""Run with HA dependencies installed: python scripts/test_colmo_core.py."""
import asyncio
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from homeassistant.exceptions import HomeAssistantError
from custom_components.midea_auto_cloud.data_coordinator import MideaDataUpdateCoordinator
from custom_components.midea_auto_cloud.button import MideaButtonEntity
from custom_components.midea_auto_cloud.device_mapping.T0xE1 import DEVICE_MAPPING

MODEL = DEVICE_MAPPING['76000029']


class ConfirmationTests(unittest.IsolatedAsyncioTestCase):
    def coordinator(self, refresh):
        coordinator = object.__new__(MideaDataUpdateCoordinator)
        coordinator.device = SimpleNamespace(
            capabilities=MODEL['capabilities'], _calculate_set=[],
            _default_values={'selected_program': 'standard_wash'},
            attributes={'work_status': 'order'},
            set_attributes=AsyncMock(return_value=True), refresh_status=refresh,
        )
        coordinator._track_poll_result = Mock()
        coordinator.async_set_updated_data = Mock()
        coordinator._snapshot = lambda: dict(coordinator.device.attributes)
        coordinator.mute_state_update_for_a_while = Mock()
        return coordinator

    async def test_cancel_waits_for_actual_state_and_never_mirrors_command(self):
        calls = 0
        async def refresh():
            nonlocal calls
            calls += 1
            if calls == 2:
                coordinator.device.attributes['work_status'] = 'cancel'
            return True
        coordinator = self.coordinator(AsyncMock(side_effect=refresh))
        with patch('custom_components.midea_auto_cloud.data_coordinator.asyncio.sleep', new=AsyncMock()):
            await coordinator.async_set_attributes({'work_status': 'cancel_order'})
        self.assertEqual(calls, 2)
        self.assertEqual(coordinator.device.attributes['work_status'], 'cancel')

    async def test_unconfirmed_command_is_bounded_and_draft_stays_local(self):
        coordinator = self.coordinator(AsyncMock(return_value=False))
        with patch('custom_components.midea_auto_cloud.data_coordinator.asyncio.sleep', new=AsyncMock()):
            with self.assertRaises(HomeAssistantError):
                await coordinator.async_set_attributes({'work_status': 'work'})
        self.assertEqual(coordinator.device.refresh_status.await_count, MODEL["capabilities"]["confirm_status_after_control"]["attempts"])
        self.assertEqual(coordinator.device.attributes['work_status'], 'order')
        coordinator.device.set_attributes.reset_mock()
        coordinator.device.refresh_status.reset_mock()
        await coordinator.async_set_attributes({'selected_program': 'eco_wash'})
        coordinator.device.set_attributes.assert_not_awaited()
        coordinator.device.refresh_status.assert_not_awaited()
        self.assertEqual(coordinator.device.attributes['selected_program'], 'eco_wash')

    async def test_legacy_mapping_keeps_existing_behavior(self):
        coordinator = self.coordinator(AsyncMock())
        coordinator.device.capabilities = {}
        await coordinator.async_set_attributes({'work_status': 'cancel'})
        coordinator.device.refresh_status.assert_not_awaited()
        self.assertEqual(coordinator.device.attributes['work_status'], 'cancel')

    async def test_reservation_powers_on_before_sending_delay(self):
        entity = object.__new__(MideaButtonEntity)
        entity._config = MODEL['entities']['button']['reserve']
        entity._entity_key = 'reserve'
        entity._device = None
        state = {'work_status': 'power_off', 'selected_program': 'standard_wash',
                 'selected_region': 3, 'selected_additional': 0, 'reservation_delay_minutes': 210}
        entity._get_nested_value = state.get
        async def send(command):
            if command == {'work_status': 'power_on'}:
                state['work_status'] = 'cancel'
        entity.async_set_attributes = AsyncMock(side_effect=send)
        await entity.async_press()
        self.assertEqual(entity.async_set_attributes.await_args_list[0].args[0], {'work_status': 'power_on'})
        self.assertEqual(entity.async_set_attributes.await_args_list[1].args[0], {
            'work_status': 'order', 'mode': 'standard_wash', 'wash_region': 3,
            'additional': 0, 'order_set_hour': 3, 'order_set_min': 30,
        })
        state['work_status'] = 'order'
        with self.assertRaises(HomeAssistantError):
            await entity.async_press()

    def test_model_polarity_and_translation_enums(self):
        self.assertEqual(MODEL['entities']['binary_sensor']['doorswitch']['rationale'], [1, 0])
        for lang in ('en', 'zh-Hans'):
            translated = json.loads((ROOT/'custom_components/midea_auto_cloud/translations'/f'{lang}.json').read_text())['entity']
            for platform, entities in MODEL['entities'].items():
                for config in entities.values():
                    self.assertIn(config['translation_key'], translated[platform])
        self.assertFalse(MODEL['cloud_queries']['water_power'])


if __name__ == '__main__':
    unittest.main()
