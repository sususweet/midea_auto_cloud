"""Boundary and routing tests; run with Home Assistant dependencies installed."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from custom_components.midea_auto_cloud.core.dishwasher import parse_usage, parse_filter_quality
import voluptuous as vol
from custom_components.midea_auto_cloud.core.cloud import MeijuCloud
from custom_components.midea_auto_cloud.device_mapping.T0xE1 import DEVICE_MAPPING
from custom_components.midea_auto_cloud.device_mapping._cloud_stats import merge_cloud_stats_mapping
from custom_components.midea_auto_cloud.data_coordinator import MideaDataUpdateCoordinator


class StatisticsTests(unittest.IsolatedAsyncioTestCase):
    def test_decimal_sum_and_boundary_validation(self):
        usage = parse_usage({'data': [
            {'yElectricity': '0.1', 'yWater': '1.1', 'washTimes': 1},
            {'yElectricity': '0.2', 'yWater': '2.2', 'washTimes': 2},
        ], 'savedWater': '4.2'})
        self.assertEqual((usage.energy_kwh, usage.water_l, usage.saved_water_l, usage.washes), (0.3, 3.3, 4.2, 3))
        with self.assertRaises(vol.Invalid):
            parse_usage({'data': [{'yElectricity': '1'}], 'savedWater': '0'})
        with self.assertRaises(vol.Invalid):
            parse_usage({'data': [], 'savedWater': '-1'})
        for minutes, expected in [(600, 'excellent'), (601, 'good'), (3000, 'good'), (3001, 'poor')]:
            self.assertEqual(parse_filter_quality({'time': minutes}), expected)
        with self.assertRaises(ValueError):
            parse_filter_quality({'time': -1})

    async def test_jykt_supports_both_success_envelopes(self):
        cloud = object.__new__(MeijuCloud)
        cloud._auto_relogin_on_token_invalid = False
        cloud._access_token = None
        cloud._api_url = 'https://example.invalid'
        cloud._proxy = None
        cloud._security = SimpleNamespace(sign=Mock(return_value='test'))
        for envelope in ['retCode', 'errCode']:
            cloud._session = SimpleNamespace(request=AsyncMock(return_value=SimpleNamespace(
                read=AsyncMock(return_value=json.dumps({envelope: 0, 'result': {'ok': True}}).encode())
            )))
            self.assertEqual(await cloud._jykt_api_request('/test', {}), {'ok': True})

    async def test_only_capable_mapping_uses_dishwasher_statistics(self):
        coordinator = object.__new__(MideaDataUpdateCoordinator)
        cloud = SimpleNamespace()
        coordinator.device = SimpleNamespace(capabilities=DEVICE_MAPPING['76000029']['capabilities'],
                                             _cloud_queries=DEVICE_MAPPING['76000029']['cloud_queries'])
        coordinator._cloud = cloud
        coordinator._last_cloud_poll = {}
        coordinator._poll_dishwasher_statistics = AsyncMock()
        coordinator._poll_dishwasher_preferences = AsyncMock()
        coordinator._poll_cloud_water_power = AsyncMock()
        await coordinator._poll_cloud_stats()
        coordinator._poll_dishwasher_statistics.assert_awaited_once()
        coordinator._poll_cloud_water_power.assert_not_awaited()
        merged = merge_cloud_stats_mapping(DEVICE_MAPPING['76000029'], 0xE1)
        self.assertEqual(merged['entities']['sensor']['filter_quality']['options'], ['excellent', 'good', 'poor'])
        legacy = merge_cloud_stats_mapping(DEVICE_MAPPING['default'], 0xE1)
        self.assertNotIn('filter_quality', legacy['entities']['sensor'])


if __name__ == '__main__':
    unittest.main()
