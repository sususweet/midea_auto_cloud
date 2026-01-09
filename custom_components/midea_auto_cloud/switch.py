from homeassistant.components.switch import SwitchEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
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
    """Set up switch entities for Midea devices."""
    account_bucket = hass.data.get(DOMAIN, {}).get("accounts", {}).get(config_entry.entry_id)
    if not account_bucket:
        async_add_entities([])
        return
    device_list = account_bucket.get("device_list", {})
    coordinator_map = account_bucket.get("coordinator_map", {})

    devs = []

    # Create device-specific switch entities
    for device_id, info in device_list.items():
        device_type = info.get("type")
        sn8 = info.get("sn8")
        config = await load_device_config(hass, device_type, sn8) or {}
        entities_cfg = (config.get("entities") or {}).get(Platform.SWITCH, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaSwitchEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))

    # Create global polling control switch (only once per account)
    # This switch controls polling for all devices under this account
    if coordinator_map:
        global_switch = GlobalPollingControlSwitch(hass, config_entry, coordinator_map)
        devs.append(global_switch)
        MideaLogger.debug(f"Created global polling control switch for account {config_entry.entry_id}")

    async_add_entities(devs)


class MideaSwitchEntity(MideaEntity, SwitchEntity):
    """Midea switch entity."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        # Automatically detect if this is a central AC device (T0x21)
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
            await self._async_set_status_on_off(attribute, True)

    async def async_turn_off(self):
        """Turn the switch off."""
        attribute = self._config.get("attribute", self._entity_key)
        if self._is_central_ac:
            await self._async_set_central_ac_switch_status(False)
        else:
            await self._async_set_status_on_off(attribute, False)

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


class GlobalPollingControlSwitch(SwitchEntity):
    """Global polling control switch for all Midea devices."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, coordinators: dict):
        """Initialize the global polling control switch.

        Args:
            hass: Home Assistant instance
            config_entry: Config entry for this integration
            coordinators: Dictionary of all coordinators {device_id: coordinator}
        """
        self.hass = hass
        self._config_entry = config_entry
        self._coordinators = coordinators
        self._attr_name = "Polling Control"
        self._attr_unique_id = f"{DOMAIN}_global_polling_control"
        self._attr_icon = "mdi:refresh-circle"
        self._is_on = True  # Default to enabled (polling active)

        # Device info for the global switch
        from homeassistant.helpers.device_registry import DeviceInfo
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "global_control")},
            name="Midea Global Control",
            manufacturer="Midea",
            model="Global Control"
        )

    @property
    def is_on(self) -> bool:
        """Return true if polling is enabled."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn on polling for all devices."""
        from datetime import timedelta

        # Resume polling for all coordinators
        for device_id, coordinator in self._coordinators.items():
            coordinator.update_interval = timedelta(seconds=30)
            MideaLogger.debug(f"Polling resumed for device {device_id}")

        self._is_on = True
        self.async_write_ha_state()
        MideaLogger.debug("Global polling enabled for all devices")

    async def async_turn_off(self, **kwargs):
        """Turn off polling for all devices."""
        # Pause polling for all coordinators
        for device_id, coordinator in self._coordinators.items():
            coordinator.update_interval = None
            MideaLogger.debug(f"Polling paused for device {device_id}")

        self._is_on = False
        self.async_write_ha_state()
        MideaLogger.debug("Global polling disabled for all devices")
