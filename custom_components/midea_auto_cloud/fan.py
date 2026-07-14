from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .climate import _add_fan_only_derived_fan
from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


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
        self._power_rationale = self._config.get("rationale")
        self._key_preset_modes = self._config.get("preset_modes")
        speeds_config = self._config.get("speeds")
        # 处理范围形式的 speeds 配置: {"key": "gear", "value": [1, 9]}
        if isinstance(speeds_config, list) and speeds_config:
            if isinstance(speeds_config[0], dict) and "key" in speeds_config[0]:
                key_name = speeds_config[0]["key"]
                value_range = speeds_config[0].get("value", [1, 100])
                if isinstance(value_range, list) and len(value_range) == 2:
                    start, end = value_range[0], value_range[1]
                    self._key_speeds = [{key_name: str(i)} for i in range(start, end + 1)]
                else:
                    self._key_speeds = speeds_config
            else:
                self._key_speeds = speeds_config
        elif isinstance(speeds_config, dict) and "key" in speeds_config and "value" in speeds_config:
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
        # 部分风扇摇头开值为 default/diy，而非 on（如 T0xFA lr_shake_switch）
        self._oscillate_rationale = self._config.get("oscillate_rationale") or self._rationale
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
        if self._key_oscillate is not None and self._oscillate_supported():
            features |= FanEntityFeature.OSCILLATE
        if self._key_directions is not None and len(self._key_directions) > 0:
            features |= FanEntityFeature.DIRECTION
        return features

    def _oscillate_supported(self) -> bool:
        """Show oscillate only when device reports capability or state attribute."""
        en_key = f"en_{self._key_oscillate}"
        en_val = self._get_nested_value(en_key)
        if en_val is not None:
            return self._get_status_on_off(en_key)
        return self._get_nested_value(self._key_oscillate) is not None

    @property
    def is_on(self) -> bool:
        if self._key_power is None:
            return False
        value = self._get_nested_value(self._key_power)
        if value is None:
            return False
        rationale = self._fan_rationale()
        try:
            return bool(rationale.index(value))
        except ValueError:
            if isinstance(value, int) or value in ("0", "1"):
                return int(value) != 0
            return False

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
        if self._key_oscillate is None:
            return False
        value = self._get_nested_value(self._key_oscillate)
        if value is None:
            return False
        rationale = self._oscillate_rationale
        off_value = rationale[0] if rationale else "off"
        if value == off_value or value in ("invalid", "unknown"):
            return False
        try:
            return bool(rationale.index(value))
        except ValueError:
            # diy/normal 等非 off 状态均视为摇头开启
            return True

    @property
    def current_direction(self):
        return self._dict_get_selected(self._key_directions)

    def _fan_rationale(self) -> list:
        return self._power_rationale or self._rationale

    async def _async_set_fan_power(self, turn_on: bool) -> None:
        if self._key_power is None:
            return
        rationale = self._fan_rationale()
        await self.async_set_attribute(self._key_power, rationale[int(turn_on)])

    def _get_speed_index_from_percentage(self, percentage: int) -> int:
        if not self._current_speeds or self._attr_speed_count == 0:
            return -1
        if self._attr_speed_count == 1:
            return 0
        index = round(percentage * self._attr_speed_count / 100) - 1
        return max(0, min(index, self._attr_speed_count - 1))

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

        await self._async_set_fan_power(True)
        if new_status:
            await self.async_set_attributes(new_status)

    async def async_turn_off(self):
        await self._async_set_fan_power(False)

    async def async_set_percentage(self, percentage: int):
        if not self._current_speeds:
            return

        if percentage == 0:
            await self.async_turn_off()
            return

        if not self.is_on:
            await self._async_set_fan_power(True)

        index = self._get_speed_index_from_percentage(percentage)
        if index >= 0:
            await self.async_set_attributes(self._current_speeds[index])

    async def async_set_preset_mode(self, preset_mode: str):
        if not self._key_preset_modes:
            return
    
        mode_config = self._key_preset_modes.get(preset_mode, {})
        if mode_config:

            # 如果风扇当前是关闭状态，先打开风扇
            if not self.is_on:
                await self._async_set_fan_power(True)

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
        if self._key_oscillate is None or self.oscillating == oscillating:
            return
        rationale = self._oscillate_rationale
        await self.async_set_attribute(self._key_oscillate, rationale[int(oscillating)])

    async def async_set_direction(self, direction: str):
        if not self._key_directions:
            return
        new_status = self._key_directions.get(direction)
        if new_status:
            await self.async_set_attributes(new_status)
