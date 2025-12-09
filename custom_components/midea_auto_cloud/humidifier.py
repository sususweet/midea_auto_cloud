from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierDeviceClass, HumidifierEntityFeature
)
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .midea_entity import MideaEntity
from . import load_device_config
from .core.logger import MideaLogger  # 新增导入

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up humidifier entities for Midea devices."""
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
        entities_cfg = (config.get("entities") or {}).get(Platform.HUMIDIFIER, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaHumidifierEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))
    async_add_entities(devs)


class MideaHumidifierEntity(MideaEntity, HumidifierEntity):
    """Generic humidifier entity."""

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
        self._attr_supported_features = HumidifierEntityFeature.MODES
        self._attr_available_modes = list(self._config.get("modes").keys())

        # 新增：外部湿度传感器支持
        external_map = self._config.get("external_humidity_sensor_map", {})
        self._has_external_sensor = self._sn8 in external_map
        if self._has_external_sensor:
            self._external_sensor_id = external_map[self._sn8]
            MideaLogger.info(f"{self.entity_id} (sn8: {self._sn8}) 设备当前使用外部湿度传感器：{self._external_sensor_id}")  #jesusya新增
        else:
            MideaLogger.info(f"{self.entity_id} (sn8: {self._sn8}) 设备当前使用加湿器内置湿度传感器。如需外接更高精度传感器，可在midea_auto_cloud/device_mapping/T0xFD.py文件中编辑 'external_humidity_sensor_map' 部分进行配置")  #jesusya新增
        

    @property
    def device_class(self):
        """Return the device class."""
        return self._config.get("device_class", HumidifierDeviceClass.HUMIDIFIER)

    @property
    def is_on(self):
        """Return if the humidifier is on."""
        power_key = self._config.get("power")
        if power_key:
            value = self.device_attributes.get(power_key)
            if isinstance(value, bool):
                return value
            return value == 1 or value == "on" or value == "true"
        return False

    @property
    def target_humidity(self):
        """Return the target humidity (30-80%), fallback to 55 if invalid or missing. 2025-11-18"""
        key = self._config.get("target_humidity")
        if not key:
            return 55

        value = self.device_attributes.get(key)
        # 如果设备没返回、返回 None 或不在合理范围，强制使用 55
        if value is None or not (30 <= value <= 80):
            return 55

        return value

    @property
    def current_humidity(self):
        """Return the current humidity."""
        # 改用新代码，支持外部湿度传感器 jesusya
        if self._has_external_sensor:  
            state = self.hass.states.get(self._external_sensor_id)  
            if state and state.state not in (None, "unknown", "unavailable"):  
                try:  
                    new_humidity = round(float(state.state))  
                    self._current_humidity = new_humidity  
                    MideaLogger.debug(f"{self.entity_id} using external sensor humidity from {self._external_sensor_id}: {self._current_humidity}")  
                    return self._current_humidity  
                except (ValueError, TypeError, AttributeError) as e:  
                    MideaLogger.warning(f"{self.entity_id} failed to parse external sensor state from {self._external_sensor_id}: {e}")  
            else:  
                MideaLogger.debug(f"{self.entity_id} external sensor {self._external_sensor_id} unavailable")  
        
        # 回退到内部传感器或直接使用内部传感器  
        current_humidity_key = self._config.get("current_humidity")  
        if current_humidity_key:  
            humidity = self.device_attributes.get(current_humidity_key, 0)  
            MideaLogger.debug(f"{self.entity_id} using internal humidity: {humidity}")  
            return humidity  
        MideaLogger.debug(f"{self.entity_id} no current_humidity_key found, returning 0")  
        return 0 

    @property
    def min_humidity(self):
        """Return the minimum humidity."""
        return self._config.get("min_humidity", 30)

    @property
    def max_humidity(self):
        """Return the maximum humidity."""
        return self._config.get("max_humidity", 80)

    @property
    def mode(self):
        """Return the current mode."""
        mode_key = self._config.get("mode")
        if mode_key:
            return self.device_attributes.get(mode_key, "sleep")
        return "sleep" #sleep 最安静，手动模式有3个风速，在这里无法设置

    @property
    def available_modes(self):
        """Return the available modes."""
        modes = self._config.get("modes", {})
        return list(modes.keys())

    async def async_turn_on(self, **kwargs):
        """Turn the humidifier on."""
        power_key = self._config.get("power")
        if power_key:
            await self._device.set_attribute(power_key, self._rationale[int(True)])

    async def async_turn_off(self, **kwargs):
        """Turn the humidifier off."""
        power_key = self._config.get("power")
        airDry_on_off_key = self._config.get("airDry_on_off")
        
        #由2次关机，改为先关闭风干湿帘，再关闭加湿器
        if power_key:
            await self._device.set_attribute(airDry_on_off_key, self._rationale[int(False)]) #避免美的加湿器，关机后设备会自动启动风干湿帘，噪音过大
            await self._device.set_attribute(power_key, self._rationale[int(False)]) 

    async def async_set_humidity(self, humidity: int):
        """Set the target humidity."""
        target_humidity_key = self._config.get("target_humidity")
        if target_humidity_key:
            await self._device.set_attribute(target_humidity_key, humidity)

    async def async_set_mode(self, mode: str):
        """Set the mode."""
        mode_key = self._config.get("mode")
        modes = self._config.get("modes", {})
        if mode_key and mode in modes:
            mode_config = modes[mode]
            for attr_key, attr_value in mode_config.items():
                await self._device.set_attribute(attr_key, attr_value)
