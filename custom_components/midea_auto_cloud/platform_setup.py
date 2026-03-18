from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import load_device_config
from .const import DOMAIN


EntityFactory = Callable[
    [Any, Any, Any, Any, str, dict[str, Any]],  # coordinator, device, manufacturer, rationale, entity_key, ecfg
    Any,
]
PerDeviceHook = Callable[[list[Any], Any, Any, Any, Any, dict[str, Any]], None]


async def async_setup_platform_entities(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    platform: Platform,
    entity_factory: EntityFactory,
    *,
    per_device_hook: PerDeviceHook | None = None,
) -> None:
    """Shared account-entry setup: iterate devices, load mapping, create entities."""
    account_bucket = hass.data.get(DOMAIN, {}).get("accounts", {}).get(config_entry.entry_id)
    if not account_bucket:
        async_add_entities([])
        return

    device_list = account_bucket.get("device_list", {})
    coordinator_map = account_bucket.get("coordinator_map", {})

    entities: list[Any] = []
    for device_id, info in device_list.items():
        device_type = info.get("type")
        sn8 = info.get("sn8")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        subtype = device.subtype if device else None
        category = device.category if device else None

        config = await load_device_config(hass, device_type, sn8, subtype, category) or {}
        entities_cfg = (config.get("entities") or {}).get(platform, {}) or {}
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")

        if per_device_hook:
            per_device_hook(entities, coordinator, device, manufacturer, rationale, config)

        for entity_key, ecfg in entities_cfg.items():
            entities.append(entity_factory(coordinator, device, manufacturer, rationale, entity_key, ecfg))

    async_add_entities(entities)

