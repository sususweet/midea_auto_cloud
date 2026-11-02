"""Unit tests for mapping_overlay (no Home Assistant install required)."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from enum import Enum
from pathlib import Path


def _install_ha_stubs() -> None:
    if "homeassistant" in sys.modules:
        return

    class Platform(str, Enum):
        CLIMATE = "climate"
        SWITCH = "switch"
        SENSOR = "sensor"
        SELECT = "select"
        BINARY_SENSOR = "binary_sensor"
        FAN = "fan"
        LIGHT = "light"
        NUMBER = "number"
        BUTTON = "button"
        COVER = "cover"
        LOCK = "lock"
        TEXT = "text"
        HUMIDIFIER = "humidifier"
        WATER_HEATER = "water_heater"
        VACUUM = "vacuum"

    ha = types.ModuleType("homeassistant")
    ha_const = types.ModuleType("homeassistant.const")
    ha_const.Platform = Platform
    ha_core = types.ModuleType("homeassistant.core")

    class HomeAssistant:  # noqa: D401 - stub
        """Minimal stub."""

    ha_core.HomeAssistant = HomeAssistant
    ha_util = types.ModuleType("homeassistant.util")
    ha_util_json = types.ModuleType("homeassistant.util.json")

    def load_json(path, default=None):
        try:
            with open(path, encoding="utf-8") as fp:
                return json.load(fp)
        except FileNotFoundError:
            return {} if default is None else default

    def save_json(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

    ha_util_json.load_json = load_json
    ha_util_json.save_json = save_json
    ha_helpers = types.ModuleType("homeassistant.helpers")
    ha_helpers_json = types.ModuleType("homeassistant.helpers.json")
    ha_helpers_json.save_json = save_json

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.const"] = ha_const
    sys.modules["homeassistant.core"] = ha_core
    sys.modules["homeassistant.util"] = ha_util
    sys.modules["homeassistant.util.json"] = ha_util_json
    sys.modules["homeassistant.helpers"] = ha_helpers
    sys.modules["homeassistant.helpers.json"] = ha_helpers_json


def _load_mapping_overlay():
    _install_ha_stubs()
    package_root = Path(__file__).resolve().parents[1]

    # Stub package pieces used by mapping_overlay imports.
    pkg = types.ModuleType("midea_auto_cloud")
    pkg.__path__ = [str(package_root)]
    sys.modules["midea_auto_cloud"] = pkg

    const_mod = types.ModuleType("midea_auto_cloud.const")
    const_mod.STORAGE_MAPPING_PATH = ".storage/midea_auto_cloud/mappings"
    const_mod.OVERRIDES_FILENAME = "overrides.json"
    sys.modules["midea_auto_cloud.const"] = const_mod

    core_pkg = types.ModuleType("midea_auto_cloud.core")
    core_pkg.__path__ = [str(package_root / "core")]
    sys.modules["midea_auto_cloud.core"] = core_pkg
    logger_mod = types.ModuleType("midea_auto_cloud.core.logger")

    class MideaLogger:
        @staticmethod
        def warning(msg):
            pass

        @staticmethod
        def info(msg):
            pass

    logger_mod.MideaLogger = MideaLogger
    sys.modules["midea_auto_cloud.core.logger"] = logger_mod

    path = package_root / "mapping_overlay.py"
    spec = importlib.util.spec_from_file_location(
        "midea_auto_cloud.mapping_overlay", path
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["midea_auto_cloud.mapping_overlay"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


mo = _load_mapping_overlay()
Platform = sys.modules["homeassistant.const"].Platform


class FakeConfig:
    def __init__(self, base: str):
        self._base = base

    def path(self, *parts: str) -> str:
        return os.path.join(self._base, *parts)


class FakeHass:
    def __init__(self, base: str):
        self.config = FakeConfig(base)


class MappingOverlayTests(unittest.TestCase):
    def test_deep_merge_and_none_delete(self):
        base = {
            "entities": {
                Platform.CLIMATE: {
                    "thermostat": {
                        "fan_modes": {"1": {"a": 1}, "2": {"b": 2}},
                        "keep": True,
                    }
                },
                Platform.SWITCH: {"power": {"attribute": "power"}},
            },
            "queries": [{"query_type": ["power"]}],
        }
        overlay = {
            "entities": {
                Platform.CLIMATE: {
                    "thermostat": {
                        "fan_modes": {"1": {"a": 9}},
                    }
                },
                Platform.SWITCH: None,
            },
            "queries": [{"query_type": ["status"]}],
        }
        merged = mo.deep_merge_mapping(base, overlay)
        self.assertEqual(
            merged["entities"][Platform.CLIMATE]["thermostat"]["fan_modes"]["1"]["a"],
            9,
        )
        self.assertEqual(
            merged["entities"][Platform.CLIMATE]["thermostat"]["fan_modes"]["2"]["b"],
            2,
        )
        self.assertTrue(merged["entities"][Platform.CLIMATE]["thermostat"]["keep"])
        self.assertNotIn(Platform.SWITCH, merged["entities"])
        self.assertEqual(merged["queries"], [{"query_type": ["status"]}])

    def test_normalize_platform_keys(self):
        mapping = {
            "entities": {
                "climate": {"thermostat": {"power": "power"}},
                "switch": {"led": {"attribute": "screen_display"}},
            }
        }
        normalized = mo.normalize_platform_keys(mapping)
        self.assertIn(Platform.CLIMATE, normalized["entities"])
        self.assertIn(Platform.SWITCH, normalized["entities"])
        # str Enum compares equal to its value; check concrete key types.
        self.assertTrue(
            all(isinstance(key, Platform) for key in normalized["entities"])
        )

    def test_validate_and_parse(self):
        self.assertEqual(
            mo.validate_profile_payload({"profile": "bad id!", "mapping": {}}),
            "invalid_profile_id",
        )
        self.assertEqual(
            mo.validate_profile_payload(
                {"profile": "ok", "mode": "nope", "mapping": {}}
            ),
            "invalid_profile_mode",
        )
        good = {
            "profile": "clivet_wall",
            "mode": "extend",
            "mapping": {"entities": {}},
        }
        self.assertIsNone(mo.validate_profile_payload(good))
        payload, err = mo.parse_profile_json_text(json.dumps(good))
        self.assertIsNone(err)
        self.assertEqual(payload["profile"], "clivet_wall")
        _, err2 = mo.parse_profile_json_text("{not-json")
        self.assertEqual(err2, "invalid_profile_json")

    def test_apply_extend_replace_and_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            hass = FakeHass(tmp)
            builtin = {
                "entities": {
                    Platform.CLIMATE: {
                        "thermostat": {"fan_modes": {"1": {"x": 1}, "2": {"y": 2}}}
                    }
                }
            }
            out = mo.apply_device_overlay(hass, builtin, "111")
            self.assertEqual(
                out["entities"][Platform.CLIMATE]["thermostat"]["fan_modes"]["2"]["y"],
                2,
            )

            extend_profile = {
                "profile": "ext1",
                "mode": "extend",
                "mapping": {
                    "entities": {
                        "climate": {"thermostat": {"fan_modes": {"1": {"x": 8}}}}
                    }
                },
            }
            self.assertIsNone(mo.save_profile(hass, extend_profile))
            self.assertIsNone(mo.set_device_override(hass, "111", "ext1"))
            extended = mo.apply_device_overlay(hass, builtin, 111)
            self.assertEqual(
                extended["entities"][Platform.CLIMATE]["thermostat"]["fan_modes"]["1"][
                    "x"
                ],
                8,
            )
            self.assertEqual(
                extended["entities"][Platform.CLIMATE]["thermostat"]["fan_modes"]["2"][
                    "y"
                ],
                2,
            )

            replace_profile = {
                "profile": "rep1",
                "mode": "replace",
                "mapping": {
                    "entities": {"climate": {"thermostat": {"fan_modes": {"9": {}}}}}
                },
            }
            self.assertIsNone(mo.save_profile(hass, replace_profile))
            self.assertIsNone(mo.set_device_override(hass, "222", "rep1"))
            replaced = mo.apply_device_overlay(hass, builtin, "222")
            self.assertEqual(
                list(
                    replaced["entities"][Platform.CLIMATE]["thermostat"][
                        "fan_modes"
                    ].keys()
                ),
                ["9"],
            )

            mo.clear_device_override(hass, "111")
            self.assertNotIn("111", mo.load_overrides(hass))
            self.assertIn("ext1", mo.list_profiles(hass))


if __name__ == "__main__":
    unittest.main()
