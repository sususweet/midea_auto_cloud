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
            new_status.update({"mode": mode_config.get("mode")})
        
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
            new_status = {"mode": mode_config.get("mode")}
        
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