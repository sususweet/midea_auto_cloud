"""Tests for independently queried preferences and staged ion drying controls."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from custom_components.midea_auto_cloud.core.dishwasher import parse_preferences
from custom_components.midea_auto_cloud.data_coordinator import MideaDataUpdateCoordinator
from custom_components.midea_auto_cloud.device_mapping.T0xE1 import DEVICE_MAPPING
from custom_components.midea_auto_cloud.button import MideaButtonEntity
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol

MODEL = DEVICE_MAPPING['76000029']


class SpecialTests(unittest.IsolatedAsyncioTestCase):
    def button(self, key, state):
        entity = object.__new__(MideaButtonEntity)
        entity._config = MODEL['entities']['button'][key]
        entity._entity_key = key
        entity._device = SimpleNamespace(device_type=0xE1, capabilities=MODEL['capabilities'])
        entity._get_nested_value = state.get
        return entity

    def test_preferences_are_distinct_and_validate_once(self):
        preference = parse_preferences({'switch': 1}, {'mode': 'win'})
        self.assertEqual((preference.smart_storage, preference.seasonal_mode), (1, 'win'))
        with self.assertRaises(vol.Invalid):
            parse_preferences({'switch': 3}, {'mode': 'auto'})
        with self.assertRaises(vol.Invalid):
            parse_preferences({'switch': 0}, {'mode': 'unrecognized'})

    async def test_duration_is_prepared_before_start(self):
        state = {'work_status': 'cancel', 'selected_ion_hours': 2, 'air_left_hour': 0}
        entity = self.button('ion_start', state)
        async def send(command):
            state.update(command)
            if command == {'airswitch': 2}:
                state['air_left_hour'] = 2
        entity.async_set_attributes = AsyncMock(side_effect=send)
        await entity.async_press()
        self.assertEqual([call.args[0] for call in entity.async_set_attributes.await_args_list],
                         [{'air_set_hour': 2}, {'airswitch': 2}])
        with self.assertRaises(HomeAssistantError):
            entity._require_idle()

    async def test_failed_duration_confirmation_never_starts(self):
        entity = self.button('ion_start', {'work_status': 'cancel', 'selected_ion_hours': 1})
        entity.async_set_attributes = AsyncMock()
        with self.assertRaises(HomeAssistantError):
            await entity.async_press()
        entity.async_set_attributes.assert_awaited_once_with({'air_set_hour': 1})

    async def test_stop_rechecks_all_three_fields_and_retries_once(self):
        state = {'work_status': 'power_off', 'airswitch': 1, 'air_left_hour': 1, 'air_status': 1}
        entity = self.button('ion_stop', state)
        async def send(command):
            if entity.async_set_attributes.await_count == 2:
                state.update(airswitch=0, air_left_hour=0, air_status=0)
        entity.async_set_attributes = AsyncMock(side_effect=send)
        await entity.async_press()
        self.assertEqual(entity.async_set_attributes.await_count, 2)
        entity.async_set_attributes = AsyncMock()
        state.update(airswitch=1, air_left_hour=1)
        with self.assertRaises(HomeAssistantError):
            await entity.async_press()
        self.assertEqual(entity.async_set_attributes.await_count, 2)

    async def test_cloud_preference_write_uses_independent_readback(self):
        coordinator = object.__new__(MideaDataUpdateCoordinator)
        coordinator._device_id = 1
        coordinator.device = SimpleNamespace(capabilities=MODEL['capabilities'], attributes={})
        coordinator._cloud = SimpleNamespace(set_dishwasher_storage=AsyncMock())
        async def poll(cloud, now):
            coordinator.device.attributes.update(smart_storage=1)
        coordinator._poll_dishwasher_preferences = AsyncMock(side_effect=poll)
        coordinator.async_set_updated_data = Mock()
        coordinator._snapshot = Mock(return_value={})
        await coordinator.async_set_attributes({'smart_storage': 1})
        coordinator._cloud.set_dishwasher_storage.assert_awaited_once_with(1, 1)
        coordinator._poll_dishwasher_preferences.assert_awaited_once()
        coordinator._poll_dishwasher_preferences = AsyncMock()
        with self.assertRaises(HomeAssistantError):
            await coordinator.async_set_attributes({'smart_storage': 0})


if __name__ == '__main__':
    unittest.main()
