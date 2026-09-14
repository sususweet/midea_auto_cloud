"""Estimate AC power from successful cloud electricity observations."""

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import math
import time

POWER_ATTRIBUTE = "real_time_power_value"
MIN_WINDOW_SECONDS = 5 * 60
WINDOW_SECONDS = 30 * 60
CACHE_SECONDS = 60 * 60
QUERY_TIMEOUT_SECONDS = 15 * 60


def supports_power_estimation(
    device_type: int, cloud_queries: dict, attributes: dict,
) -> bool:
    """Return whether the device exposes the required AC mapping."""
    return (
        device_type == 0xAC
        and bool(cloud_queries.get("electricity"))
        and POWER_ATTRIBUTE in attributes
    )


def _number(value: object) -> float | None:
    """Return a finite, nonnegative number, excluding booleans."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


@dataclass(frozen=True)
class EnergySample:
    """An energy observation with monotonic and display timestamps."""

    elapsed: float
    sampled_at: datetime
    energy_kwh: float
    period: str


@dataclass(frozen=True)
class PowerReading:
    """A consistent snapshot of power and its provenance."""

    value: float | None
    source: str
    status: str
    window_seconds: float | None
    last_energy_sample_at: datetime | None

    def as_attributes(self) -> dict:
        """Return Home Assistant state attributes."""
        return {
            "power_source": self.source,
            "estimation_status": self.status,
            "estimation_window_seconds": self.window_seconds,
            "last_energy_sample_at": (
                self.last_energy_sample_at.isoformat()
                if self.last_energy_sample_at else None
            ),
        }


# 缺少有效实测功率时，按以下数轴估算（示例忽略云端延迟）：
# 时间       14:00     14:10     14:15     14:25     14:40
#              |         |         |         |         |
# 状态        关机 ----- 开机 --------------------------
# 电量 kWh   39.12     39.12     39.12     39.27     39.42
# 功率 W         0      未知      未知       600       600
#                        +---- 15 分钟估算 ---+
#                        +-------- 30 分钟估算 ---------+
# 开机时间与最近有效电量组成临时基线，首次增量至少间隔 5 分钟。
# 功率 W = 电量增量 kWh × 3_600_000 / 实际间隔秒数。
# 窗口逐步扩展到约 30 分钟；重复电量不移动计算终点，过期则未知。
# 关机的 0 W 是状态推定，不含待机耗电；实测值（包括 0 W）优先。
# 临时基线可能是云端旧值，首次增量可能含延迟补报，结果并非瞬时功率。
class PowerEstimator:
    """Maintain one device's estimate without accessing Home Assistant.

    Callers supply monotonic seconds for intervals and aware datetimes for
    display. Only successful electricity responses belong in observe_energy.
    """

    def __init__(
        self, clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize with a monotonic clock shared by energy observations.

        Args:
            clock: Callable returning monotonic seconds. Tests may inject a
                clock; observe_energy and resolve must use the same time base.
        """
        self._clock = clock
        self._samples: deque[EnergySample] = deque()
        self._online = False
        self._running: bool | None = None
        self._last_energy: EnergySample | None = None
        self._baseline_available = False
        self._status = "insufficient_samples"

    def _reset(self, status: str) -> None:
        self._samples.clear()
        self._status = status

    def observe_state(self, *, online: bool, running: object) -> None:
        """Observe availability and normalize the AC power switch state.

        Args:
            online: Whether the coordinator currently considers data available.
            running: Boolean or on/off string; other values mean unknown.

        Repeated states preserve the running baseline. Losing availability or
        a known switch state invalidates reuse until a fresh energy response.
        """
        state = running if isinstance(running, bool) else {
            "on": True, "off": False,
        }.get(str(running).lower())
        if not online:
            self._reset("device_unavailable")
            self._baseline_available = False
        elif state is None:
            self._reset("unknown_running_state")
            self._baseline_available = False
        elif not state:
            self._reset("assumed_off")
        elif not self._online or self._running is not True:
            self._reset("insufficient_samples")
            previous = self._last_energy
            now = self._clock()
            # 只复用刚才在线关机期间的有效电量，不能跨断线补造基线。
            if (
                self._online and self._running is False
                and self._baseline_available and previous is not None
                and 0 <= now - previous.elapsed < QUERY_TIMEOUT_SECONDS
            ):
                self._samples.append(EnergySample(
                    now, previous.sampled_at, previous.energy_kwh,
                    previous.period,
                ))
        self._online = online
        self._running = state

    def observe_energy(
        self, *, elapsed: float, sampled_at: datetime,
        energy_kwh: object, period: str,
    ) -> None:
        """Record a valid response; repeated values are not new endpoints.

        Args:
            elapsed: Monotonic seconds from the same clock used at construction.
            sampled_at: Timezone-aware acquisition time, used for diagnostics.
            energy_kwh: Cumulative monthly kWh from a successful cloud response.
            period: Month of the query, formatted as YYYY-MM.

        Invalid values do not refresh query age. A response received while
        offline or with unknown switch state cannot authorize baseline reuse.
        """
        value = _number(energy_kwh)
        if value is None:
            return
        sample = EnergySample(elapsed, sampled_at, value, period)
        previous = self._last_energy
        self._last_energy = sample
        # 保留诊断时间，但只有恢复后的有效查询才能重新授权基线复用。
        self._baseline_available = self._online and self._running is not None
        if previous is not None and (
            elapsed <= previous.elapsed
            or elapsed - previous.elapsed >= QUERY_TIMEOUT_SECONDS
            or period != previous.period
            or value < previous.energy_kwh
        ):
            self._reset("baseline_reset")
        if not self._online or self._running is not True:
            return
        if self._samples and (
            elapsed - self._samples[-1].elapsed >= WINDOW_SECONDS
        ):
            self._reset("stale_energy")
        # 查询成功只证明接口可用；相同电量无法区分低耗电和云端停更。
        if not self._samples or value != self._samples[-1].energy_kwh:
            self._samples.append(sample)
        while self._samples and (
            elapsed - self._samples[0].elapsed > CACHE_SECONDS
        ):
            self._samples.popleft()

    def resolve(
        self, *, elapsed: float, measured_power_w: object,
    ) -> PowerReading:
        """Choose measured power or an estimate for the current snapshot.

        Args:
            elapsed: Current monotonic seconds, using the observation clock.
            measured_power_w: Original measured watts, before any fallback.

        Returns:
            An immutable value and provenance snapshot. Expired sample windows
            are cleared here; callers should resolve when publishing updates,
            not each time an entity property is read.
        """
        last_at = (
            self._last_energy.sampled_at if self._last_energy else None
        )

        def reading(
            value: float | None, source: str, status: str,
            window: float | None = None,
        ) -> PowerReading:
            return PowerReading(value, source, status, window, last_at)

        if not self._online:
            return reading(None, "unavailable", "device_unavailable")
        measured = _number(measured_power_w)
        if measured is not None:
            return reading(measured, "measured", "ready")
        if self._running is False:
            return reading(0.0, "estimated", "assumed_off")
        if self._running is None:
            return reading(None, "unavailable", "unknown_running_state")
        if self._last_energy and (
            elapsed < self._last_energy.elapsed
            or elapsed - self._last_energy.elapsed >= QUERY_TIMEOUT_SECONDS
        ):
            self._reset("stale_query")
        if self._samples and (
            elapsed - self._samples[-1].elapsed >= WINDOW_SECONDS
        ):
            self._reset("stale_energy")
        if len(self._samples) >= 2:
            end = self._samples[-1]
            candidates = [
                sample for sample in self._samples
                if MIN_WINDOW_SECONDS <= end.elapsed - sample.elapsed
                <= CACHE_SECONDS
            ]
            if candidates:
                # 先取最长短窗口；成熟后取最接近且不少于 30 分钟的窗口。
                start = candidates[0]
                for candidate in reversed(candidates):
                    if end.elapsed - candidate.elapsed >= WINDOW_SECONDS:
                        start = candidate
                        break
                duration = end.elapsed - start.elapsed
                watts = (
                    (end.energy_kwh - start.energy_kwh)
                    * 3_600_000 / duration
                )
                status = "warming_up" if duration < WINDOW_SECONDS else "ready"
                return reading(watts, "estimated", status, duration)
        return reading(None, "unavailable", self._status)
