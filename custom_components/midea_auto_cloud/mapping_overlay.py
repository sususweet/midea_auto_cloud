"""External mapping overlay: per-device_id profiles under .storage.

Profiles and overrides survive HACS upgrades because they live outside
custom_components. Options UI and hand-edited files share the same layout.
"""

from __future__ import annotations

import copy
import json
import os
import re
from typing import Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.util.json import load_json

try:
    from homeassistant.helpers.json import save_json
except ImportError:
    from homeassistant.util.json import save_json

from .const import OVERRIDES_FILENAME, STORAGE_MAPPING_PATH
from .core.logger import MideaLogger

_PROFILE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_VALID_MODES = frozenset({"extend", "replace"})

# Platform.value -> Platform for JSON string keys
_PLATFORM_BY_VALUE: dict[str, Platform] = {p.value: p for p in Platform}


def mappings_dir(hass: HomeAssistant) -> str:
    return hass.config.path(STORAGE_MAPPING_PATH)


def overrides_path(hass: HomeAssistant) -> str:
    return os.path.join(mappings_dir(hass), OVERRIDES_FILENAME)


def profile_path(hass: HomeAssistant, profile_id: str) -> str:
    return os.path.join(mappings_dir(hass), f"{profile_id}.json")


def ensure_mappings_dir(hass: HomeAssistant) -> str:
    path = mappings_dir(hass)
    os.makedirs(path, exist_ok=True)
    return path


def normalize_device_id(device_id: str | int | None) -> str | None:
    if device_id is None:
        return None
    text = str(device_id).strip()
    return text or None


def is_valid_profile_id(profile_id: str) -> bool:
    return bool(_PROFILE_ID_RE.match(profile_id or ""))


def validate_profile_payload(payload: dict[str, Any]) -> str | None:
    """Return an error key, or None if valid."""
    if not isinstance(payload, dict):
        return "invalid_profile_json"
    profile_id = payload.get("profile")
    if not isinstance(profile_id, str) or not is_valid_profile_id(profile_id):
        return "invalid_profile_id"
    mode = payload.get("mode", "extend")
    if mode not in _VALID_MODES:
        return "invalid_profile_mode"
    mapping = payload.get("mapping")
    if not isinstance(mapping, dict):
        return "invalid_profile_mapping"
    return None


def normalize_platform_keys(mapping: dict[str, Any] | None) -> dict[str, Any]:
    """Convert string platform keys under entities to Platform enums."""
    if not mapping:
        return {}
    result = copy.deepcopy(mapping)
    entities = result.get("entities")
    if not isinstance(entities, dict):
        return result
    normalized: dict[Any, Any] = {}
    for key, value in entities.items():
        if isinstance(key, Platform):
            normalized[key] = value
            continue
        platform = _PLATFORM_BY_VALUE.get(str(key))
        if platform is not None:
            normalized[platform] = value
        else:
            # Keep unknown keys so custom keys are not silently dropped.
            normalized[key] = value
    result["entities"] = normalized
    return result


def deep_merge_mapping(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge overlay into base.

    - dict values are merged recursively
    - list / scalar values replace
    - overlay value None deletes the key from the result
    """
    result = copy.deepcopy(base) if base else {}
    if not overlay:
        return result

    for key, value in overlay.items():
        if value is None:
            result.pop(key, None)
            continue
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge_mapping(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_overrides(hass: HomeAssistant) -> dict[str, str]:
    path = overrides_path(hass)
    raw = load_json(path, default={})
    if not isinstance(raw, dict):
        return {}
    overrides: dict[str, str] = {}
    for device_id, profile_id in raw.items():
        did = normalize_device_id(device_id)
        if did and isinstance(profile_id, str) and is_valid_profile_id(profile_id):
            overrides[did] = profile_id
    return overrides


def save_overrides(hass: HomeAssistant, overrides: dict[str, str]) -> None:
    ensure_mappings_dir(hass)
    cleaned = {
        str(device_id): profile_id
        for device_id, profile_id in overrides.items()
        if normalize_device_id(device_id) and is_valid_profile_id(profile_id)
    }
    save_json(overrides_path(hass), cleaned)


def load_profile(hass: HomeAssistant, profile_id: str) -> dict[str, Any] | None:
    if not is_valid_profile_id(profile_id):
        return None
    path = profile_path(hass, profile_id)
    raw = load_json(path, default={})
    if not isinstance(raw, dict) or not raw:
        return None
    return raw


def save_profile(hass: HomeAssistant, payload: dict[str, Any]) -> str | None:
    """Validate and write a profile. Returns error key or None on success."""
    error = validate_profile_payload(payload)
    if error:
        return error
    ensure_mappings_dir(hass)
    profile_id = payload["profile"]
    to_save = {
        "profile": profile_id,
        "mode": payload.get("mode", "extend"),
        "mapping": payload["mapping"],
    }
    if "device_type" in payload:
        to_save["device_type"] = payload["device_type"]
    save_json(profile_path(hass, profile_id), to_save)
    return None


def list_profiles(hass: HomeAssistant) -> list[str]:
    path = mappings_dir(hass)
    if not os.path.isdir(path):
        return []
    profiles: list[str] = []
    for name in os.listdir(path):
        if not name.endswith(".json") or name == OVERRIDES_FILENAME:
            continue
        profile_id = name[:-5]
        if is_valid_profile_id(profile_id):
            profiles.append(profile_id)
    return sorted(profiles)


def set_device_override(
    hass: HomeAssistant, device_id: str | int, profile_id: str
) -> str | None:
    did = normalize_device_id(device_id)
    if not did:
        return "invalid_device_id"
    if not is_valid_profile_id(profile_id):
        return "invalid_profile_id"
    if load_profile(hass, profile_id) is None:
        return "profile_not_found"
    overrides = load_overrides(hass)
    overrides[did] = profile_id
    save_overrides(hass, overrides)
    return None


def clear_device_override(hass: HomeAssistant, device_id: str | int) -> None:
    did = normalize_device_id(device_id)
    if not did:
        return
    overrides = load_overrides(hass)
    if did in overrides:
        overrides.pop(did)
        save_overrides(hass, overrides)


def parse_profile_json_text(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """Parse pasted JSON. Returns (payload, error_key)."""
    try:
        payload = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None, "invalid_profile_json"
    if not isinstance(payload, dict):
        return None, "invalid_profile_json"
    error = validate_profile_payload(payload)
    if error:
        return None, error
    return payload, None


def apply_device_overlay(
    hass: HomeAssistant,
    builtin: dict[str, Any] | None,
    device_id: str | int | None,
) -> dict[str, Any]:
    """Apply per-device profile overlay on top of builtin mapping."""
    base = copy.deepcopy(builtin) if builtin else {}
    did = normalize_device_id(device_id)
    if not did:
        return base

    overrides = load_overrides(hass)
    profile_id = overrides.get(did)
    if not profile_id:
        return base

    profile = load_profile(hass, profile_id)
    if not profile:
        MideaLogger.warning(
            f"Mapping overlay: profile '{profile_id}' for device {did} not found"
        )
        return base

    mode = profile.get("mode", "extend")
    overlay_mapping = normalize_platform_keys(profile.get("mapping") or {})

    if mode == "replace":
        MideaLogger.info(
            f"Mapping overlay: replace builtin with profile '{profile_id}' "
            f"for device {did}"
        )
        return overlay_mapping

    MideaLogger.info(
        f"Mapping overlay: extend builtin with profile '{profile_id}' "
        f"for device {did}"
    )
    return deep_merge_mapping(base, overlay_mapping)
