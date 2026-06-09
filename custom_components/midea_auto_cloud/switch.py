from homeassistant.components.switch import SwitchEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities for Midea devices."""
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.SWITCH,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaSwitchEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaSwitchEntity(MideaEntity, SwitchEntity):
    """Midea switch entity."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        # 自动判断是否为中央空调设备（T0x21）
        self._is_central_ac = device.device_type == 0x21
        
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

    @property
    def is_on(self) -> bool:
        """Return if the switch is on."""
        # Use attribute from config if available, otherwise fall back to entity_key
        attribute = self._config.get("attribute", self._entity_key)
        return self._get_status_on_off(attribute)

    async def async_turn_on(self):
        """Turn the switch on."""
        attribute = self._config.get("attribute", self._entity_key)
        if self._is_central_ac:
            await self._async_set_central_ac_switch_status(True)
        else:
            await self._async_set_switch_status(attribute, True)

    async def async_turn_off(self):
        """Turn the switch off."""
        attribute = self._config.get("attribute", self._entity_key)
        if self._is_central_ac:
            await self._async_set_central_ac_switch_status(False)
        else:
            await self._async_set_switch_status(attribute, False)

    async def _async_set_switch_status(self, attribute: str | None, turn_on: bool):
        """Set switch status, merging fixed command parameters if configured."""
        if attribute is None:
            return
        command = self._config.get("command")
        if command and isinstance(command, dict):
            merged_command = {**command, attribute: self._rationale[int(turn_on)]}
            await self.async_set_attributes(merged_command)
        else:
            await self._async_set_status_on_off(attribute, turn_on)

    async def _async_set_central_ac_switch_status(self, is_on: bool):
        """设置中央空调开关设备的状态"""
        # 从entity_key中提取endpoint ID
        # entity_key格式: endpoint_1_OnOff -> 提取出 1
        endpoint_id = 1  # 默认值
        if self._entity_key.startswith("endpoint_"):
            try:
                # 提取endpoint_后面的数字
                parts = self._entity_key.split("_")
                if len(parts) >= 2:
                    endpoint_id = int(parts[1])
            except (ValueError, IndexError):
                MideaLogger.warning(f"Failed to extract endpoint ID from {self._entity_key}, using default 1")
        
        # 构建控制命令
        control = {
            "run_mode": "1" if is_on else "0",
            "endpoint": endpoint_id
        }
        await self.coordinator.async_send_switch_control(control)
