from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
    VacuumActivity,
)
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
    """Set up vacuum entities for Midea devices."""
    # 账号型 entry：从 __init__ 写入的 accounts 桶加载设备和协调器
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
        entities_cfg = (config.get("entities") or {}).get(Platform.VACUUM, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None

        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaVacuumEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))
    async_add_entities(devs)

class MideaVacuumEntity(MideaEntity, StateVacuumEntity):
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
        self._key_battery_level = self._config.get("battery_level")
        self._key_control = self._config.get("control")
        self._key_fan_speeds = self._config.get("fan_speeds")
        self._control_actions = self._config.get("control_actions", {})
        #self._key_locate = self._config.get("locate")
        #self._key_clean_spot = self._config.get("clean_spot")
        #self._key_map = self._config.get("map")

    @property
    def supported_features(self):
        features = VacuumEntityFeature(0)
        features |= VacuumEntityFeature.STOP
        features |= VacuumEntityFeature.PAUSE
        features |= VacuumEntityFeature.START
        features |= VacuumEntityFeature.RETURN_HOME
        features |= VacuumEntityFeature.FAN_SPEED
        features |= VacuumEntityFeature.STATUS
        features |= VacuumEntityFeature.BATTERY
        #features |= VacuumEntityFeature.LOCATE
        #features |= VacuumEntityFeature.CLEAN_SPOT
        #features |= VacuumEntityFeature.MAP
        return features

    @property
    def battery_level(self):
        """Return the battery level of the vacuum cleaner."""
        battery = self._get_nested_value(self._key_battery_level)
        if battery is not None:
            try:
                return int(battery)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def status(self):
        """Return the status of the vacuum cleaner."""
        status = self._get_nested_value(self._key_control)
        if status is not None:
            return status
        return None

    @property
    def state(self):
        """Return the state of the vacuum cleaner."""
        status = self.status
        if not status:
            return None

        # Map Midea status to Home Assistant states
        status_mapping = {
            # === 清洁中状态 (CLEANING) ===
            "work": VacuumActivity.CLEANING,           # 清扫中
            "auto_clean": VacuumActivity.CLEANING,     # 自动清扫中

            # === 已停靠状态 (DOCKED) ===
            "charging_on_dock": VacuumActivity.DOCKED, # 座充中
            "on_base": VacuumActivity.DOCKED,          # 在基站上
            "charge_finish": VacuumActivity.DOCKED,    # 充电完成

            # === 空闲状态 (IDLE) ===
            "stop": VacuumActivity.IDLE,               # 已停止
            "sleep": VacuumActivity.IDLE,              # 休眠中

            # === 暂停状态 (PAUSED) ===
            "clean_pause": VacuumActivity.PAUSED,      # 清扫暂停
            "charge_pause": VacuumActivity.PAUSED,     # 充电暂停

            # === 返回中状态 (RETURNING) ===
            "charging": VacuumActivity.RETURNING,      # 返回基站中

            # === 错误状态 (ERROR) ===
            "error": VacuumActivity.ERROR,             # 错误
        }

        return status_mapping.get(status, status)

    @property
    def fan_speed(self):
        """Return the current fan speed."""
        return self._dict_get_selected(self._key_fan_speeds)

    @property
    def fan_speed_list(self):
        """Return the list of available fan speeds."""
        return list(self._key_fan_speeds.keys())

    async def _async_set_control(self, action: str, default_value: str):
        """Set control with action mapping and fallback."""
        control_value = self._control_actions.get(action, default_value)
        await self.async_set_attribute(self._key_control, control_value)

    async def async_start(self):
        """Start or resume the cleaning task."""
        # 设置为工作状态
        if self._key_control:
            await self._async_set_control("start", "work")
        else:
            await self._async_set_status_on_off(self._key_power, True)

    async def async_stop(self):
        """Stop the vacuum cleaner."""
        # 设置为停止状态
        if self._key_control:
            await self._async_set_control("stop", "stop")
        else:
            await self._async_set_status_on_off(self._key_power, False)

    async def async_pause(self):
        """Pause the cleaning task."""
        # 设置为暂停状态
        if self._key_control:
            await self._async_set_control("pause", "pause")

    async def async_return_to_base(self):
        """Return the vacuum cleaner to its base."""
        # 设置为回基站状态
        if self._key_control:
            await self._async_set_control("return", "charge")

    async def async_set_fan_speed(self, fan_speed: str):
        """Set the fan speed."""
        new_status = self._key_fan_speeds.get(fan_speed)
        if new_status is not None:
            await self.async_set_attributes(new_status)

    #async def async_locate(self):
        #"""Locate the vacuum cleaner."""
        # 定位设备
        # 具体实现取决于设备的控制方式
        #if hasattr(self, "_key_locate"):
            #await self.async_set_attribute(self._key_locate, True)

    #async def async_clean_spot(self):
        #"""Perform a clean spot."""
        # 执行定点清扫
        # 具体实现取决于设备的控制方式
        #if hasattr(self, "_key_clean_spot"):
            #await self.async_set_attribute(self._key_clean_spot, True)
