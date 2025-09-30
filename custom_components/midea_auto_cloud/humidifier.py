from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierDeviceClass
)
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
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
        """Return the target humidity."""
        target_humidity_key = self._config.get("target_humidity")
        if target_humidity_key:
            return self.device_attributes.get(target_humidity_key, 0)
        return 0

    @property
    def current_humidity(self):
        """Return the current humidity."""
        current_humidity_key = self._config.get("current_humidity")
        if current_humidity_key:
            return self.device_attributes.get(current_humidity_key, 0)
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
            return self.device_attributes.get(mode_key, "manual")
        return "manual"

    @property
    def available_modes(self):
        """Return the available modes."""
        modes = self._config.get("modes", {})
        return list(modes.keys())

    async def async_turn_on(self, **kwargs):
        """Turn the humidifier on."""
        power_key = self._config.get("power")
        if power_key:
            await self._device.set_attribute(power_key, True)

    async def async_turn_off(self, **kwargs):
        """Turn the humidifier off."""
        power_key = self._config.get("power")
        if power_key:
            await self._device.set_attribute(power_key, False)

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
