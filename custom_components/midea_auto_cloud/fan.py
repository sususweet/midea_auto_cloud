from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


_NUMERIC_FAN_MODE_TO_SEMANTIC = {
    "102": "auto",
    "20": "low",
    "40": "medium_low",
    "60": "medium",
    "80": "high",
    "100": "max",
}
_SEMANTIC_FAN_MODE_TO_NUMERIC = {
    "auto": "102",
    "low": "20",
    "medium_low": "40",
    "medium": "60",
    "high": "80",
    "max": "100",
}
_MANUAL_FAN_MODE_ORDER = ["low", "medium_low", "medium", "high", "max"]
_SEMANTIC_FAN_MODE_ALIASES = {
    "silent": "low",
    "full": "max",
}
_FAN_ONLY_ENTITY_KEY = "fan_only_fan"


def _fan_mode_key_to_semantic(key) -> str | None:
    key = str(key)
    if key in _NUMERIC_FAN_MODE_TO_SEMANTIC:
        return _NUMERIC_FAN_MODE_TO_SEMANTIC[key]
    if key in _SEMANTIC_FAN_MODE_TO_NUMERIC:
        return key
    return _SEMANTIC_FAN_MODE_ALIASES.get(key)


def _build_fan_only_fan_mode_configs(fan_modes) -> dict[str, dict]:
    if fan_modes is None or not hasattr(fan_modes, "items"):
        return {}

    mode_configs = {}
    for key, value in fan_modes.items():
        semantic_mode = _fan_mode_key_to_semantic(key)
        if semantic_mode is not None:
            mode_configs[semantic_mode] = value
    return mode_configs


def _default_manual_fan_mode(manual_fan_modes: list[str]) -> str:
    if "medium_low" in manual_fan_modes:
        return "medium_low"
    if "medium" in manual_fan_modes:
        return "medium"
    return manual_fan_modes[0]


def _supports_fan_only_derived_fan(config: dict) -> bool:
    climate_entities = (config.get("entities") or {}).get(Platform.CLIMATE, {}) or {}
    for climate_config in climate_entities.values():
        hvac_modes = climate_config.get("hvac_modes") or {}
        if "fan_only" not in hvac_modes or "off" not in hvac_modes:
            continue
        fan_mode_configs = _build_fan_only_fan_mode_configs(climate_config.get("fan_modes"))
        if "auto" in fan_mode_configs and any(
            mode in fan_mode_configs for mode in _MANUAL_FAN_MODE_ORDER
        ):
            return True
    return False


def _add_fan_only_derived_fan(entities, coordinator, device, manufacturer, rationale, config):
    if coordinator is None or device is None:
        return
    if not _supports_fan_only_derived_fan(config):
        return
    entities.append(
        MideaFanOnlyFanEntity(
            coordinator,
            device,
            manufacturer,
            rationale,
            _FAN_ONLY_ENTITY_KEY,
            config,
        )
    )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.FAN,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaFanEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
        per_device_hook=_add_fan_only_derived_fan,
    )


class MideaFanOnlyFanEntity(MideaEntity, FanEntity):
    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        climate_entities = (config.get("entities") or {}).get(Platform.CLIMATE, {}) or {}
        climate_config = next(
            ecfg for ecfg in climate_entities.values()
            if _build_fan_only_fan_mode_configs(ecfg.get("fan_modes")).get("auto") is not None
            and any(
                mode in _build_fan_only_fan_mode_configs(ecfg.get("fan_modes"))
                for mode in _MANUAL_FAN_MODE_ORDER
            )
            and "fan_only" in (ecfg.get("hvac_modes") or {})
            and "off" in (ecfg.get("hvac_modes") or {})
        )
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
            config={
                "translation_key": "fan_only_fan",
            },
        )
        self._key_hvac_modes = climate_config.get("hvac_modes")
        self._fan_mode_configs = _build_fan_only_fan_mode_configs(climate_config.get("fan_modes"))
        self._manual_fan_modes = [
            mode for mode in _MANUAL_FAN_MODE_ORDER if mode in self._fan_mode_configs
        ]
        self._attr_speed_count = len(self._manual_fan_modes)

    @property
    def supported_features(self):
        return (
            FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
            | FanEntityFeature.SET_SPEED
            | FanEntityFeature.PRESET_MODE
        )

    @property
    def is_on(self) -> bool:
        return self._current_hvac_mode() == "fan_only"

    @property
    def preset_modes(self):
        return ["auto"]

    @property
    def preset_mode(self):
        if not self.is_on:
            return None
        if self._current_fan_mode() == "auto":
            return "auto"
        return None

    @property
    def percentage(self):
        if not self.is_on:
            return 0
        current_fan_mode = self._current_fan_mode()
        if current_fan_mode not in self._manual_fan_modes:
            return 0
        return round(
            (self._manual_fan_modes.index(current_fan_mode) + 1)
            * 100
            / len(self._manual_fan_modes)
        )

    async def async_turn_on(
            self,
            percentage: int | None = None,
            preset_mode: str | None = None,
            **kwargs,
    ):
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
            return
        if percentage is not None:
            await self.async_set_percentage(percentage)
            return
        await self._async_set_fan_only_mode(_default_manual_fan_mode(self._manual_fan_modes))

    async def async_turn_off(self):
        await self.async_set_attributes(self._key_hvac_modes["off"])

    async def async_set_percentage(self, percentage: int):
        if percentage <= 0:
            await self.async_turn_off()
            return
        selected_index = round(percentage * len(self._manual_fan_modes) / 100) - 1
        selected_index = max(0, min(selected_index, len(self._manual_fan_modes) - 1))
        await self._async_set_fan_only_mode(self._manual_fan_modes[selected_index])

    async def async_set_preset_mode(self, preset_mode: str):
        if preset_mode == "auto":
            await self._async_set_fan_only_mode("auto")
            return

    def _current_hvac_mode(self):
        return self._dict_get_selected(self._key_hvac_modes)

    def _current_fan_mode(self):
        selected = self._dict_get_selected(self._fan_mode_configs)
        return selected

    async def _async_set_fan_only_mode(self, fan_mode: str):
        new_status = {}
        new_status.update(self._key_hvac_modes["fan_only"])
        new_status.update(self._fan_mode_configs[fan_mode])
        await self.async_set_attributes(new_status)


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
        self._current_preset_mode = None
        self._current_speeds = self._key_speeds

    @property
    def supported_features(self):
        features = FanEntityFeature(0)
        features |= FanEntityFeature.TURN_ON
        features |= FanEntityFeature.TURN_OFF
        if self._key_preset_modes is not None and len(self._key_preset_modes) > 0:
            features |= FanEntityFeature.PRESET_MODE
        if self._current_speeds is not None and len(self._current_speeds) > 0:
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
        if self._key_preset_modes is None:
            return None
        return list(self._key_preset_modes.keys())

    @property
    def preset_mode(self):
        if self._key_preset_modes is None:
            return None
    
        current_mode = self._dict_get_selected(self._key_preset_modes)
    
        if current_mode:
            mode_config = self._key_preset_modes.get(current_mode, {})
        
            # 切换到该模式的档位配置
            if "speeds" in mode_config:
                self._current_speeds = mode_config["speeds"]
                self._attr_speed_count = len(self._current_speeds)
            else:
                # 使用全局配置
                self._current_speeds = self._key_speeds
                self._attr_speed_count = len(self._current_speeds) if self._current_speeds else 0
        
            self._current_preset_mode = current_mode
    
        return current_mode

    @property
    def percentage(self):
        # 如果风扇关闭，返回0%（这样UI会显示"关闭"）
        if not self.is_on:
            return 0

        index = self._list_get_selected(self._current_speeds)
        if index is None:
            return 0

        # 计算百分比：档位1对应最小百分比，最大档位对应100%
        if self._attr_speed_count <= 1:
            return 100  # 只有一个档位时，开启就是100%

        return round((index + 1) * 100 / self._attr_speed_count)

    @property
    def oscillating(self):
        return self._get_status_on_off(self._key_oscillate)

    @property
    def current_direction(self):
        return self._dict_get_selected(self._key_directions)

    async def async_turn_on(
            self,
            percentage: int | None = None,
            preset_mode: str | None = None,
            **kwargs,
    ):
        new_status = {}
        if preset_mode is not None and self._key_preset_modes is not None:
            mode_config = self._key_preset_modes.get(preset_mode, {})
            new_status.update(
                {key: value for key, value in mode_config.items() if key != "speeds"}
            )
        
            # 切换到该模式的档位配置
            if "speeds" in mode_config:
                self._current_speeds = mode_config["speeds"]
                self._attr_speed_count = len(self._current_speeds)
            else:
                self._current_speeds = self._key_speeds
                self._attr_speed_count = len(self._current_speeds) if self._current_speeds else 0
        
            self._current_preset_mode = preset_mode
        
            # 如果只有一个档位，自动设置
            if "speeds" in mode_config and len(mode_config["speeds"]) == 1:
                new_status.update(mode_config["speeds"][0])
    
        # 使用当前模式的速度配置
        if percentage is not None and self._current_speeds:
            # 如果百分比为0，直接关闭（但async_turn_on不应该传入0）
            if percentage == 0:
                await self.async_turn_off()
                return
                    
            # 计算档位索引（至少为1档）
            if self._attr_speed_count <= 1:
                index = 0
            else:
                index = round(percentage * self._attr_speed_count / 100) - 1
                index = max(0, min(index, len(self._current_speeds) - 1))
        
            new_status.update(self._current_speeds[index])

        # 打开风扇
        await self._async_set_status_on_off(self._key_power, True)
        if new_status:
            await self.async_set_attributes(new_status)

    async def async_turn_off(self):
        await self._async_set_status_on_off(self._key_power, False)

    async def async_set_percentage(self, percentage: int):
        if not self._current_speeds:
            return

        # 处理关闭情况（0% 表示关闭）
        if percentage == 0:
            await self.async_turn_off()
            return
        
        # 如果风扇当前是关闭状态，先打开风扇
        if not self.is_on:
            await self._async_set_status_on_off(self._key_power, True)
    
        # 将百分比转换为档位索引（从1开始，因为0%已处理）
        if self._attr_speed_count <= 1:
            index = 0
        else:
            # 百分比1-100对应档位1到最大档位
            index = round((percentage / 100) * self._attr_speed_count)
            index = max(1, min(index, self._attr_speed_count))  # 确保至少为1档
    
        # 获取对应档位的配置
        if 1 <= index <= len(self._current_speeds):
            new_status = self._current_speeds[index - 1]  # 索引从0开始，所以减1
            await self.async_set_attributes(new_status)

    async def async_set_preset_mode(self, preset_mode: str):
        if not self._key_preset_modes:
            return
    
        mode_config = self._key_preset_modes.get(preset_mode, {})
        if mode_config:

            # 如果风扇当前是关闭状态，先打开风扇
            if not self.is_on:
                await self._async_set_status_on_off(self._key_power, True)

            # 切换到该模式的档位配置
            if "speeds" in mode_config:
                self._current_speeds = mode_config["speeds"]
                self._attr_speed_count = len(self._current_speeds)
            else:
                self._current_speeds = self._key_speeds
                self._attr_speed_count = len(self._current_speeds) if self._current_speeds else 0
        
            self._current_preset_mode = preset_mode
        
            # 设置模式
            new_status = {key: value for key, value in mode_config.items() if key != "speeds"}
        
            # 如果只有一个档位，自动设置
            if "speeds" in mode_config and len(mode_config["speeds"]) == 1:
                new_status.update(mode_config["speeds"][0])
        
            await self.async_set_attributes(new_status)

    async def async_oscillate(self, oscillating: bool):
        if self.oscillating != oscillating:
            await self._async_set_status_on_off(self._key_oscillate, oscillating)

    async def async_set_direction(self, direction: str):
        if not self._key_directions:
            return
        new_status = self._key_directions.get(direction)
        if new_status:
            await self.async_set_attributes(new_status)
