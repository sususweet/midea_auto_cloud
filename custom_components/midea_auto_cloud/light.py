from homeassistant.components.light import LightEntity, LightEntityFeature, ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .core.logger import MideaLogger
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
        entities_cfg = (config.get("entities") or {}).get(Platform.LIGHT, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaLightEntity(coordinator, device, manufacturer, rationale, entity_key, ecfg))
    async_add_entities(devs)


class MideaLightEntity(MideaEntity, LightEntity):
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
        self._key_brightness = self._config.get("brightness")
        self._key_color_temp = self._config.get("color_temp")
        self._key_oscillate = self._config.get("oscillate")
        self._key_directions = self._config.get("directions")

        # 检测亮度配置类型：范围 [min, max] 或嵌套格式 {"brightness": [min, max]}
        self._brightness_is_range = False
        self._brightness_min = 0
        self._brightness_max = 255
        self._brightness_key = "brightness"  # 默认键名
        
        if self._key_brightness:
            if isinstance(self._key_brightness, list) and len(self._key_brightness) == 2:
                # 直接范围格式：[min, max]
                if isinstance(self._key_brightness[0], (int, float)) and isinstance(self._key_brightness[1], (int, float)):
                    self._brightness_is_range = True
                    self._brightness_min = self._key_brightness[0]
                    self._brightness_max = self._key_brightness[1]
            elif isinstance(self._key_brightness, dict):
                # 嵌套格式：{"brightness": [min, max]} 或其他键名
                for key, value in self._key_brightness.items():
                    if isinstance(value, list) and len(value) == 2:
                        if isinstance(value[0], (int, float)) and isinstance(value[1], (int, float)):
                            self._brightness_is_range = True
                            self._brightness_min = value[0]
                            self._brightness_max = value[1]
                            self._brightness_key = key
                            break

        # 检测色温配置类型：范围 [min_kelvin, max_kelvin] 或嵌套格式 {"color_temp": [min_kelvin, max_kelvin]}
        self._color_temp_is_range = False
        self._color_temp_min = 2700  # 默认最小色温（暖白）
        self._color_temp_max = 6500  # 默认最大色温（冷白）
        self._color_temp_key = "color_temp"  # 默认键名
        
        if self._key_color_temp:
            if isinstance(self._key_color_temp, list) and len(self._key_color_temp) == 2:
                # 直接范围格式：[min_kelvin, max_kelvin]
                if isinstance(self._key_color_temp[0], (int, float)) and isinstance(self._key_color_temp[1], (int, float)):
                    self._color_temp_is_range = True
                    self._color_temp_min = self._key_color_temp[0]
                    self._color_temp_max = self._key_color_temp[1]
            elif isinstance(self._key_color_temp, dict):
                # 嵌套格式：{"color_temp": [min_kelvin, max_kelvin]} 或其他键名
                for key, value in self._key_color_temp.items():
                    if isinstance(value, list) and len(value) == 2:
                        if isinstance(value[0], (int, float)) and isinstance(value[1], (int, float)):
                            self._color_temp_is_range = True
                            self._color_temp_min = value[0]
                            self._color_temp_max = value[1]
                            self._color_temp_key = key
                            break

    @property
    def supported_features(self):
        features = LightEntityFeature(0)
        if self._key_preset_modes is not None and len(self._key_preset_modes) > 0:
            features |= LightEntityFeature.EFFECT
        return features

    @property
    def supported_color_modes(self):
        """返回支持的色彩模式"""
        modes = set()
        if self._brightness_is_range and self._color_temp_is_range:
            modes.add(ColorMode.BRIGHTNESS)
            modes.add(ColorMode.COLOR_TEMP)
        elif self._brightness_is_range:
            modes.add(ColorMode.BRIGHTNESS)
        elif self._color_temp_is_range:
            modes.add(ColorMode.COLOR_TEMP)
        else:
            modes.add(ColorMode.ONOFF)
        return modes

    @property
    def color_mode(self):
        """返回当前色彩模式"""
        if self._brightness_is_range and self._color_temp_is_range:
            # 如果同时支持亮度和色温，优先返回色温模式
            return ColorMode.COLOR_TEMP
        elif self._brightness_is_range:
            return ColorMode.BRIGHTNESS
        elif self._color_temp_is_range:
            return ColorMode.COLOR_TEMP
        return ColorMode.ONOFF

    @property
    def is_on(self) -> bool:
        return self._get_status_on_off(self._key_power)

    @property
    def effect_list(self):
        return list(self._key_preset_modes.keys())

    @property
    def effect(self):
        return self._dict_get_selected(self._key_preset_modes)

    @property
    def brightness(self):
        """返回0-255范围内的亮度值（Home Assistant标准）"""
        if not self._brightness_is_range:
            return None
            
        # 范围模式：从设备属性读取亮度值，使用配置的键名
        brightness_value = self._get_nested_value(self._brightness_key)
        if brightness_value is not None:
            brightness_value = int(brightness_value)
        if brightness_value is not None:
            # 如果配置是[0, 255]但实际设备范围是1-100，需要特殊处理
            if self._brightness_min == 0 and self._brightness_max == 255:
                # 特殊处理：设备1-100范围映射到HA的0-255范围
                ha_brightness = round(brightness_value * 2.55)  # 1-100 -> 0-255
                return max(1, min(255, ha_brightness))
            else:
                # 正常范围映射
                device_range = self._brightness_max - self._brightness_min
                if device_range > 0:
                    ha_brightness = round((brightness_value - self._brightness_min) * 255 / device_range)
                    return max(1, min(255, ha_brightness))
        return None

    @property
    def color_temp_kelvin(self):
        """返回当前色温值（开尔文）"""
        if not self._color_temp_is_range:
            return None
            
        # 从设备属性读取色温值（1-100范围）
        color_temp_value = self._get_nested_value(self._color_temp_key)
        if color_temp_value is not None:
            try:
                device_color_temp = int(color_temp_value)
                # 将设备的1-100值转换为开尔文值
                kelvin_range = self._color_temp_max - self._color_temp_min
                if kelvin_range > 0:
                    # 将1-100范围映射回开尔文范围
                    ha_color_temp = self._color_temp_min + device_color_temp * kelvin_range / 100
                    return round(ha_color_temp)
                else:
                    return self._color_temp_min
            except (ValueError, TypeError):
                return None
        return None

    @property
    def min_color_temp_kelvin(self):
        """返回支持的最小色温值（开尔文）"""
        if self._color_temp_is_range:
            return self._color_temp_min
        return None

    @property
    def max_color_temp_kelvin(self):
        """返回支持的最大色温值（开尔文）"""
        if self._color_temp_is_range:
            return self._color_temp_max
        return None

    async def async_turn_on(
            self,
            brightness: int | None = None,
            brightness_pct: int | None = None,
            percentage: int | None = None,
            color_temp_kelvin: int | None = None,
            effect: str | None = None,
            preset_mode: str | None = None,
            **kwargs,
    ):
        new_status = {}
        # 处理预设模式/效果 - 支持 effect 和 preset_mode 参数
        selected_effect = effect or preset_mode
        MideaLogger.debug(f"effect: {effect}, preset_mode: {preset_mode}, selected_effect: {selected_effect}")
        if selected_effect is not None and self._key_preset_modes is not None:
            effect_config = self._key_preset_modes.get(selected_effect, {})
            MideaLogger.debug(f"effect_config: {effect_config}")
            new_status.update(effect_config)
        
        # 处理亮度设置 - 支持多种参数格式
        target_brightness = None
        if brightness is not None:
            # Home Assistant标准：0-255范围
            target_brightness = brightness
        elif brightness_pct is not None:
            # 百分比格式：0-100范围，转换为0-255
            target_brightness = round(brightness_pct * 255 / 100)
        elif percentage is not None:
            # 兼容旧格式：0-100范围，转换为0-255
            target_brightness = round(percentage * 255 / 100)
            
        if target_brightness is not None and self._key_brightness and self._brightness_is_range:
            # 范围模式：将Home Assistant的0-255映射到设备范围
            # 如果配置是[0, 255]但实际设备范围是1-100，需要特殊处理
            if self._brightness_min == 0 and self._brightness_max == 255:
                # 特殊处理：配置[0,255]但实际设备范围是1-100
                device_brightness = round(target_brightness / 2.55)  # 0-255 -> 0-100
                device_brightness = max(1, min(100, device_brightness))  # 确保在1-100范围内
            else:
                # 正常范围映射
                device_range = self._brightness_max - self._brightness_min
                if device_range > 0:
                    device_brightness = round(self._brightness_min + (target_brightness / 255.0) * device_range)
                    device_brightness = max(self._brightness_min, min(self._brightness_max, device_brightness))
                else:
                    return
            new_status[self._brightness_key] = device_brightness
        
        # 处理色温设置
        if color_temp_kelvin is not None and self._color_temp_is_range:
            # 确保色温值在配置的范围内
            ha_color_temp = max(self._color_temp_min, min(self._color_temp_max, color_temp_kelvin))
            
            # 将开尔文值转换为设备范围（1-100）
            kelvin_range = self._color_temp_max - self._color_temp_min
            if kelvin_range > 0:
                # 将开尔文值映射到1-100范围
                device_color_temp = round((ha_color_temp - self._color_temp_min) * 100 / kelvin_range)
                device_color_temp = max(0, min(100, device_color_temp))
            else:
                device_color_temp = 50  # 默认中间值
            
            new_status[self._color_temp_key] = str(device_color_temp)
                
        await self._async_set_status_on_off(self._key_power, True)
        if new_status:
            await self.async_set_attributes(new_status)

    async def async_turn_off(self):
        await self._async_set_status_on_off(self._key_power, False)
