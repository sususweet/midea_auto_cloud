from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .midea_entity import MideaEntity
from . import load_device_config


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    account_bucket = hass.data.get(DOMAIN, {}).get("accounts", {}).get(config_entry.entry_id)
    if not account_bucket:
        async_add_entities([])
        return
    device_list = account_bucket.get("device_list", {})
    coordinator_map = account_bucket.get("coordinator_map", {})

    devs = []
    for device_id, info in device_list.items():
        device_type = info.get("type")
        sn8 = info.get("sn8")
        config = await load_device_config(hass, device_type, sn8) or {}
        entities_cfg = (config.get("entities") or {}).get(Platform.FAN, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaFanEntity(coordinator, device, manufacturer, rationale, entity_key, ecfg))
    async_add_entities(devs)


class MideaFanEntity(MideaEntity, FanEntity):
    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        super().__init__(
            coordinator,
            device.device_id,
            device.device_name,
            f"T0x{device.device_type:02X}",
            device.sn,
            device.sn8,
            device.model,
            entity_key,
            device=device,
            manufacturer=manufacturer,
            rationale=rationale,
            config=config,
        )
        self._key_power = self._config.get("power")
        self._key_preset_modes = self._config.get("preset_modes")
        speeds_config = self._config.get("speeds")
        # 处理范围形式的 speeds 配置: {"key": "gear", "value": [1, 9]}
        if isinstance(speeds_config, dict) and "key" in speeds_config and "value" in speeds_config:
            key_name = speeds_config["key"]
            value_range = speeds_config["value"]
            if isinstance(value_range, list) and len(value_range) == 2:
                start, end = value_range[0], value_range[1]
                self._key_speeds = [{key_name: str(i)} for i in range(start, end + 1)]
            else:
                self._key_speeds = speeds_config
        else:
            self._key_speeds = speeds_config
        self._key_oscillate = self._config.get("oscillate")
        self._key_directions = self._config.get("directions")
        self._attr_speed_count = len(self._key_speeds) if self._key_speeds else 0

    @property
    def supported_features(self):
        features = FanEntityFeature(0)
        features |= FanEntityFeature.TURN_ON
        features |= FanEntityFeature.TURN_OFF
        if self._key_preset_modes is not None and len(self._key_preset_modes) > 0:
            features |= FanEntityFeature.PRESET_MODE
        if self._key_speeds is not None and len(self._key_speeds) > 0:
            features |= FanEntityFeature.SET_SPEED
        if self._key_oscillate is not None:
            features |= FanEntityFeature.OSCILLATE
        if self._key_directions is not None and len(self._key_directions) > 0:
            features |= FanEntityFeature.DIRECTION
        return features

    @property
    def is_on(self) -> bool:
        return self._get_status_on_off(self._key_power)

    @property
    def preset_modes(self):
        return list(self._key_preset_modes.keys())

    @property
    def preset_mode(self):
        return self._dict_get_selected(self._key_preset_modes)

    @property
    def percentage(self):
        index = self._list_get_selected(self._key_speeds)
        if index is None:
            return None
        return round((index + 1) * 100 / self._attr_speed_count)

    @property
    def oscillating(self):
        return self._get_status_on_off(self._key_oscillate)

    async def async_turn_on(
            self,
            percentage: int | None = None,
            preset_mode: str | None = None,
            **kwargs,
    ):
        new_status = {}
        if preset_mode is not None and self._key_preset_modes is not None:
            new_status.update(self._key_preset_modes.get(preset_mode, {}))
        if percentage is not None and self._key_speeds:
            index = round(percentage * self._attr_speed_count / 100) - 1
            index = max(0, min(index, len(self._key_speeds) - 1))
            new_status.update(self._key_speeds[index])
        await self._async_set_status_on_off(self._key_power, True)
        if new_status:
            await self.async_set_attributes(new_status)

    async def async_turn_off(self):
        await self._async_set_status_on_off(self._key_power, False)

    async def async_set_percentage(self, percentage: int):
        if not self._key_speeds:
            return
        index = round(percentage * self._attr_speed_count / 100)
        if 0 < index <= len(self._key_speeds):
            new_status = self._key_speeds[index - 1]
            await self.async_set_attributes(new_status)

    async def async_set_preset_mode(self, preset_mode: str):
        if not self._key_preset_modes:
            return
        new_status = self._key_preset_modes.get(preset_mode)
        if new_status:
            await self.async_set_attributes(new_status)

    async def async_oscillate(self, oscillating: bool):
        if self.oscillating != oscillating:
            await self._async_set_status_on_off(self._key_oscillate, oscillating)

