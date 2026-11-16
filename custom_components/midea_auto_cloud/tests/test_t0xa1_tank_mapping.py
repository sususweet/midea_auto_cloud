"""T0xA1 tank binary sensor must turn on at the reported full level (no HA install required)."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

MAPPING = (
    Path(__file__).resolve().parents[1] / "device_mapping" / "T0xA1.py"
)


def _load_mapping():
    stubs = {
        name: mock.MagicMock()
        for name in (
            "homeassistant",
            "homeassistant.const",
            "homeassistant.components",
            "homeassistant.components.humidifier",
            "homeassistant.components.sensor",
            "homeassistant.components.binary_sensor",
            "homeassistant.components.switch",
        )
    }
    with mock.patch.dict(sys.modules, stubs):
        spec = importlib.util.spec_from_file_location("t0xa1_mapping_under_test", MAPPING)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.DEVICE_MAPPING, stubs["homeassistant.const"].Platform.BINARY_SENSOR


class TankStatusMappingTest(unittest.TestCase):
    def test_every_profile_maps_full_level_to_on(self):
        mapping, binary_sensor = _load_mapping()
        checked = 0
        for name, profile in mapping.items():
            tank = profile["entities"].get(binary_sensor, {}).get("tank_status")
            if tank is None:
                continue
            checked += 1
            self.assertEqual(tank.get("rationale"), [0, 100], name)
        self.assertGreaterEqual(checked, 3)


if __name__ == "__main__":
    unittest.main()
