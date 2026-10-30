"""Decode dishwasher-specific cloud statistics at the vendor boundary."""
from dataclasses import dataclass
from decimal import Decimal
import voluptuous as vol

_USAGE = vol.Schema({
    vol.Required("data"): [vol.Schema({
        vol.Required("yElectricity"): vol.All(vol.Coerce(Decimal), vol.Range(min=0)),
        vol.Required("yWater"): vol.All(vol.Coerce(Decimal), vol.Range(min=0)),
        vol.Required("washTimes"): vol.All(vol.Coerce(int), vol.Range(min=0)),
    }, extra=vol.ALLOW_EXTRA)],
    vol.Required("savedWater"): vol.All(vol.Coerce(Decimal), vol.Range(min=0)),
}, extra=vol.ALLOW_EXTRA)
_FILTER = vol.Schema({vol.Required("time"): vol.Coerce(int)}, extra=vol.ALLOW_EXTRA)

@dataclass(frozen=True)
class Usage:
    energy_kwh: float
    water_l: float
    saved_water_l: float
    washes: int


def parse_usage(payload: object) -> Usage:
    value = _USAGE(payload)
    return Usage(
        float(sum((row["yElectricity"] for row in value["data"]), Decimal(0))),
        float(sum((row["yWater"] for row in value["data"]), Decimal(0))),
        float(value["savedWater"]),
        sum(row["washTimes"] for row in value["data"]),
    )


def parse_filter_quality(payload: object) -> str:
    minutes = _FILTER(payload)["time"]
    if minutes < 0:
        raise ValueError("Negative dishwasher filter usage")
    return "excellent" if minutes <= 600 else "good" if minutes <= 3000 else "poor"


_STORAGE = vol.Schema({vol.Required("switch"): vol.In([0, 1])}, extra=vol.ALLOW_EXTRA)
_SEASON = vol.Schema({vol.Required("mode"): vol.In(["auto", "win", "sum"])}, extra=vol.ALLOW_EXTRA)

@dataclass(frozen=True)
class Preferences:
    smart_storage: int
    seasonal_mode: str


def parse_preferences(storage: object, season: object) -> Preferences:
    """Validate vendor-owned preference payloads once at their boundary."""
    return Preferences(int(_STORAGE(storage)["switch"]), _SEASON(season)["mode"])
