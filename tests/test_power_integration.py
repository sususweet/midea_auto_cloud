"""Test power fallback with real Home Assistant classes and mocked I/O."""

from datetime import datetime
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.midea_auto_cloud.data_coordinator import (
    MideaDataUpdateCoordinator,
    MideaDeviceData,
)
from custom_components.midea_auto_cloud.midea_entity import MideaEntity
from custom_components.midea_auto_cloud.power_estimation import (
    POWER_ATTRIBUTE,
    PowerEstimator,
)
from custom_components.midea_auto_cloud.sensor import MideaSensorEntity


class PowerIntegrationTest(unittest.IsolatedAsyncioTestCase):
    """Keep module imports, constructors, inheritance and listeners intact."""

    async def asyncSetUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.hass = HomeAssistant(self.directory.name)
        attributes = {"power": "off", POWER_ATTRIBUTE: None, "temperature": 25}
        self.device = SimpleNamespace(
            device_id=1, device_name="Test AC", device_type=0xAC,
            attributes=attributes, _attributes=attributes,
            _cloud_queries={"electricity": {"interval": 300}},
            _refresh_interval=20, _ip_address=None, connected=True,
            sn="test-sn", sn8="12345678", model="Test model",
            register_update=Mock(), refresh_status=AsyncMock(return_value=True),
        )
        self.cloud = SimpleNamespace(query_electricity=AsyncMock(
            return_value={"totalValue": "10"},
        ))
        self.coordinator = MideaDataUpdateCoordinator(
            self.hass, None, self.device, cloud=self.cloud,
        )
        self.addAsyncCleanup(self.coordinator.async_shutdown)
        self.now = 0
        self.assertIsInstance(self.coordinator.power_estimator, PowerEstimator)
        self.coordinator.power_estimator = PowerEstimator(
            clock=lambda: self.now,
        )
        self.clock_patch = patch(
            "custom_components.midea_auto_cloud.data_coordinator.time",
            SimpleNamespace(monotonic=lambda: self.now),
        )

    def sensor(self, key=POWER_ATTRIBUTE):
        entity = MideaSensorEntity(
            self.coordinator, self.device, "Midea", None, key, {},
        )
        self.addAsyncCleanup(entity._debounced_publish_command.async_shutdown)
        return entity

    async def test_initialization_snapshot_and_entity_inheritance(self):
        self.assertIsInstance(self.coordinator, DataUpdateCoordinator)
        with self.clock_patch:
            self.coordinator.data = await self.coordinator.poll_device_state()
        sensor = self.sensor()
        self.assertIsInstance(sensor, SensorEntity)
        self.assertIsInstance(sensor, MideaEntity)
        self.assertEqual(sensor.native_value, 0)
        self.assertTrue(sensor.available)
        self.assertEqual(sensor.extra_state_attributes["estimation_status"],
                         "assumed_off")
        self.assertEqual(self.sensor("temperature").native_value, 25)
        snapshot = self.coordinator.data
        self.device.attributes["temperature"] = 26
        self.assertEqual(snapshot.attributes["temperature"], 25)
        self.assertIsNone(snapshot.attributes[POWER_ATTRIBUTE])

    async def test_poll_observes_transition_before_energy_and_copies_once(self):
        with self.clock_patch:
            self.coordinator.data = await self.coordinator.poll_device_state()
        self.now = 100
        self.device.attributes["power"] = "on"
        # Start with a state callback; cloud sample arrives five minutes later.
        with self.clock_patch:
            self.coordinator._device_update_callback({"power": "on"})
        self.now = 400
        self.cloud.query_electricity.return_value = {"totalValue": "10.05"}
        self.coordinator._last_cloud_poll.clear()
        listener = Mock()
        remove = self.coordinator.async_add_listener(listener)
        self.addCleanup(remove)
        with self.clock_patch, patch.object(
            self.coordinator, "_snapshot", wraps=self.coordinator._snapshot,
        ) as snapshot:
            await self.coordinator.async_refresh()
        self.assertEqual(snapshot.call_count, 1)
        listener.assert_called_once()
        sensor = self.sensor()
        self.assertAlmostEqual(sensor.native_value, 600)
        self.assertEqual(sensor.extra_state_attributes["power_source"],
                         "estimated")
        before = self.coordinator.data
        _ = sensor.native_value, sensor.extra_state_attributes
        self.assertIs(self.coordinator.data, before)
        self.assertIsNone(self.device.attributes[POWER_ATTRIBUTE])

    async def test_poll_only_opening_observes_state_before_month_response(self):
        with self.clock_patch:
            self.coordinator.data = await self.coordinator.poll_device_state()
        self.now = 400
        self.device.attributes["power"] = "on"
        self.cloud.query_electricity.return_value = {"totalValue": "10.05"}
        self.coordinator._last_cloud_poll.clear()
        with self.clock_patch:
            self.coordinator.data = await self.coordinator.poll_device_state()
        sensor = self.sensor()
        self.assertEqual(sensor.native_value, 0)
        self.assertEqual(sensor.extra_state_attributes["power_source"], "held")
        self.assertEqual(
            sensor.extra_state_attributes["estimation_status"], "warming_up",
        )
        self.now = 700
        self.cloud.query_electricity.return_value = {"totalValue": "10.1"}
        self.coordinator._last_cloud_poll.clear()
        with self.clock_patch:
            self.coordinator.data = await self.coordinator.poll_device_state()
        # The opening baseline is 10, not the 10.05 response from that poll.
        self.assertAlmostEqual(self.sensor().native_value, 1200)

    async def test_sensor_preserves_inherited_attributes(self):
        self.coordinator.data = self.coordinator._snapshot()
        sensor = self.sensor()
        inherited = {"existing": "preserved"}
        with patch.object(
            MideaEntity, "extra_state_attributes", new_callable=PropertyMock,
            return_value=inherited,
        ):
            attributes = sensor.extra_state_attributes
            self.assertEqual(attributes["existing"], "preserved")
            self.assertEqual(attributes["estimation_status"], "assumed_off")
            self.assertEqual(inherited, {"existing": "preserved"})
            self.assertEqual(
                self.sensor("temperature").extra_state_attributes, inherited,
            )

    async def test_month_success_survives_year_failure(self):
        self.coordinator._observe_power_state()
        self.cloud.query_electricity.side_effect = [
            {"totalValue": "12.5"}, RuntimeError("year failed"),
        ]
        with self.assertLogs(
            "custom_components.midea_auto_cloud.data_coordinator", "WARNING",
        ), self.clock_patch:
            await self.coordinator._poll_cloud_electricity(
                self.cloud, datetime.now(),
            )
        self.assertEqual(
            self.device.attributes["cloud_electricity_month"], 12.5,
        )
        previous = self.coordinator.power_estimator._last_energy
        self.cloud.query_electricity.side_effect = None
        self.cloud.query_electricity.return_value = None
        self.now = 300
        with self.clock_patch:
            await self.coordinator._poll_cloud_electricity(
                self.cloud, datetime.now(),
            )
        self.assertIs(self.coordinator.power_estimator._last_energy, previous)

    async def test_unavailable_and_measured_priority(self):
        self.device.attributes[POWER_ATTRIBUTE] = 3
        self.coordinator.data = self.coordinator._snapshot()
        sensor = self.sensor()
        self.assertEqual(sensor.native_value, 3)
        self.coordinator._consecutive_poll_failures = 3
        self.coordinator.data = self.coordinator._snapshot()
        self.assertFalse(sensor.available)
        self.assertIsNone(sensor.native_value)

    async def test_unsupported_device_and_legacy_payload(self):
        self.device.device_type = 0xDA
        coordinator = MideaDataUpdateCoordinator(
            self.hass, None, self.device, cloud=self.cloud,
        )
        self.addAsyncCleanup(coordinator.async_shutdown)
        self.assertIsNone(coordinator.power_estimator)
        self.assertIsNone(coordinator._snapshot().power_reading)
        self.assertIsNone(MideaDeviceData({}, True, True).power_reading)


if __name__ == "__main__":
    unittest.main()
