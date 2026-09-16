"""Deterministic tests for cloud power estimation without HA dependencies."""

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components/midea_auto_cloud/power_estimation.py"
)
SPEC = importlib.util.spec_from_file_location("power_estimation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PowerEstimatorTest(unittest.TestCase):
    """Exercise energy timing and state boundaries with an explicit clock."""

    def setUp(self):
        self.now = 0
        self.estimator = MODULE.PowerEstimator(clock=lambda: self.now)
        self.estimator.observe_state(online=True, running="on")
        self.origin = datetime(2026, 9, 14, tzinfo=timezone.utc)

    def sample(self, seconds, value, period="2026-09"):
        self.estimator.observe_energy(
            elapsed=seconds,
            sampled_at=self.origin + timedelta(seconds=seconds),
            energy_kwh=value,
            period=period,
        )

    def warm(self):
        for seconds in range(0, 1801, 300):
            self.sample(seconds, 10 + (seconds // 900) * 0.1)

    def result(self, seconds=1800, measured=None):
        return self.estimator.resolve(
            elapsed=seconds, measured_power_w=measured,
        )

    def test_average_and_repeated_energy(self):
        self.warm()
        result = self.result()
        self.assertAlmostEqual(result.value, 400)
        self.assertEqual(result.window_seconds, 1800)
        self.sample(2100, 10.2)
        self.assertAlmostEqual(self.result(2100).value, 400)
        self.assertEqual(self.result(2100).source, "estimated")

    def test_warmup_and_isolation(self):
        self.warm()
        other = MODULE.PowerEstimator()
        other.observe_state(online=True, running="on")
        self.assertIsNone(other.resolve(
            elapsed=1800, measured_power_w=None,
        ).value)
        self.assertIsNotNone(self.result().value)

    def test_measured_zero_and_invalid_values(self):
        self.warm()
        for measured in (0, "0", 700, "700"):
            with self.subTest(measured=measured):
                self.assertEqual(self.result(measured=measured).source,
                                 "measured")
        for measured in (True, -1, "invalid", "nan", float("inf")):
            with self.subTest(measured=measured):
                self.assertEqual(self.result(measured=measured).source,
                                 "estimated")

    def test_query_timeout(self):
        self.warm()
        self.assertEqual(self.result(2700).status, "stale_query")
        self.sample(2701, 11)
        self.assertIsNone(self.result(2701).value)

    def test_unchanged_energy_expires(self):
        self.warm()
        for seconds in range(2100, 3601, 300):
            self.sample(seconds, 10.2)
        self.assertIsNone(self.result(3600).value)

    def test_period_and_counter_reset(self):
        for value, period in ((0, "2026-09"), (11, "2026-10")):
            with self.subTest(period=period):
                self.setUp()
                self.warm()
                self.sample(2100, value, period)
                self.assertIsNone(self.result(2100).value)

    def test_off_state_and_measured_priority(self):
        self.estimator.observe_state(online=True, running="off")
        self.assertEqual(self.result().value, 0)
        self.assertEqual(self.result().status, "assumed_off")
        self.assertEqual(self.result(measured=3).value, 3)
        self.assertEqual(self.result(measured=3).source, "measured")
        self.estimator.observe_state(online=False, running="off")
        self.assertIsNone(self.result().value)

    def test_timeline_uses_opening_time_and_first_increment(self):
        self.estimator.observe_state(online=True, running="off")
        self.sample(0, 39.12)
        self.sample(300, 39.12)
        self.assertEqual(self.result(300).value, 0)
        self.now = 600
        self.estimator.observe_state(online=True, running="on")
        result = self.result(600)
        self.assertEqual(result.value, 0)
        self.assertEqual(result.source, "held")
        self.assertEqual(result.status, "warming_up")
        self.assertIsNone(result.window_seconds)
        self.sample(800, 39.14)
        self.assertEqual(self.result(800).value, 0)
        self.assertEqual(self.result(800).source, "held")
        for seconds in (900, 1200):
            self.sample(seconds, 39.14)
        self.sample(1500, 39.27)
        result = self.result(1500)
        self.assertAlmostEqual(result.value, 600)
        self.assertEqual(result.window_seconds, 900)
        self.assertEqual(result.status, "warming_up")
        for seconds in (1800, 2100):
            self.sample(seconds, 39.27)
        self.sample(2400, 39.42)
        self.assertAlmostEqual(self.result(2400).value, 600)
        self.assertEqual(self.result(2400).window_seconds, 1800)
        self.assertEqual(self.result(2400).status, "ready")
        self.estimator.observe_state(online=True, running="off")
        self.assertEqual(self.result(2400).value, 0)

    def test_cold_start_does_not_invent_a_held_value(self):
        result = self.result(0)
        self.assertIsNone(result.value)
        self.assertEqual(result.source, "unavailable")
        self.assertEqual(result.status, "insufficient_samples")

    def test_minimum_window_and_short_window_growth(self):
        self.sample(0, 10)
        self.sample(120, 10.02)
        self.assertIsNone(self.result(120).value)
        self.sample(300, 10.05)
        self.assertAlmostEqual(self.result(300).value, 600)
        self.assertEqual(self.result(300).window_seconds, 300)
        self.sample(600, 10.1)
        self.assertEqual(self.result(600).window_seconds, 600)

    def test_stale_off_baseline_and_repeated_on_state(self):
        self.estimator.observe_state(online=True, running="off")
        self.sample(0, 10)
        self.assertEqual(self.result(0).value, 0)
        self.now = 1000
        self.estimator.observe_state(online=True, running="on")
        self.sample(1000, 10.2)
        # A stale baseline is reset rather than hidden by a held value.
        self.assertIsNone(self.result(1000).value)
        self.now = 1200
        self.estimator.observe_state(online=True, running="on")
        self.sample(1300, 10.25)
        self.assertAlmostEqual(self.result(1300).value, 600)

    def test_offline_and_unknown_state(self):
        self.warm()
        self.estimator.observe_state(online=False, running="on")
        self.assertIsNone(self.result(measured=500).value)
        self.estimator.observe_state(online=True, running=None)
        self.assertEqual(self.result().status, "unknown_running_state")
        self.assertEqual(self.result(measured=0).value, 0)

    def test_offline_recovery_requires_fresh_baseline(self):
        self.sample(0, 10)
        self.estimator.observe_state(online=False, running="on")
        self.now = 200
        self.estimator.observe_state(online=True, running="off")
        self.now = 210
        self.estimator.observe_state(online=True, running="on")
        self.sample(510, 10.1)
        self.assertIsNone(self.result(510).value)
        self.sample(810, 10.15)
        self.assertAlmostEqual(self.result(810).value, 600)

    def test_offline_samples_cannot_authorize_baseline(self):
        self.sample(0, 10)
        self.estimator.observe_state(online=False, running="off")
        self.sample(100, 10.1)
        self.estimator.observe_state(online=True, running="off")
        self.now = 200
        self.estimator.observe_state(online=True, running="on")
        self.sample(500, 10.2)
        self.assertIsNone(self.result(500).value)

    def test_fresh_off_sample_after_recovery_authorizes_baseline(self):
        self.sample(0, 10)
        self.estimator.observe_state(online=False, running="on")
        self.estimator.observe_state(online=True, running="off")
        self.sample(200, 10.1)
        self.now = 210
        self.estimator.observe_state(online=True, running="on")
        self.sample(510, 10.15)
        self.assertAlmostEqual(self.result(510).value, 600)

    def test_unknown_state_invalidates_baseline(self):
        self.sample(0, 10)
        self.estimator.observe_state(online=True, running=None)
        self.estimator.observe_state(online=True, running="off")
        self.now = 200
        self.estimator.observe_state(online=True, running="on")
        self.sample(500, 10.1)
        self.assertIsNone(self.result(500).value)

    def test_invalid_energy_is_not_a_success(self):
        self.sample(0, 10)
        for value in (True, -1, "NaN", "bad", None):
            self.sample(300, value)
        self.assertEqual(self.estimator._last_energy.elapsed, 0)

    def test_irregular_interval_and_cache_bound(self):
        for seconds in range(0, 8001, 320):
            self.sample(seconds, 10 + (seconds // 960) * 0.08)
        result = self.result(8000)
        self.assertAlmostEqual(result.value, 300)
        self.assertEqual(result.window_seconds, 1920)
        self.assertTrue(all(
            8000 - sample.elapsed <= MODULE.CACHE_SECONDS
            for sample in self.estimator._samples
        ))

    def test_clock_regression_resets(self):
        self.warm()
        self.sample(1700, 10.3)
        self.assertIsNone(self.result(1700).value)

    def test_support_and_attributes(self):
        self.assertTrue(MODULE.supports_power_estimation(
            0xAC, {"electricity": {"interval": 300}},
            {MODULE.POWER_ATTRIBUTE: None},
        ))
        self.assertFalse(MODULE.supports_power_estimation(0xAC, {}, {}))
        self.warm()
        attributes = self.result().as_attributes()
        self.assertEqual(attributes["power_source"], "estimated")
        self.assertIn("+00:00", attributes["last_energy_sample_at"])


if __name__ == "__main__":
    unittest.main()
