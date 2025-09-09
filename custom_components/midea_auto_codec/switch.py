from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (
    Platform,
    CONF_DEVICE_ID,
    CONF_ENTITIES, CONF_DEVICE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    DEVICES
)
from .midea_entity import MideaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities for Midea devices."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_data = hass.data[DOMAIN][DEVICES][device_id]
    coordinator = device_data.get("coordinator")
    device = device_data.get(CONF_DEVICE)
    manufacturer = device_data.get("manufacturer")
    rationale = device_data.get("rationale")
    entities = device_data.get(CONF_ENTITIES, {}).get(Platform.SWITCH, {})
    
    devs = []
    if entities:
        for entity_key, config in entities.items():
            devs.append(MideaSwitchEntity(
                coordinator, device, manufacturer, rationale, entity_key, config
            ))
    async_add_entities(devs)


class MideaSwitchEntity(MideaEntity, SwitchEntity):
    """Midea switch entity."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        super().__init__(
            coordinator,
            device.device_id,
            device.device_name,
            f"T0x{device.device_type:02X}",
            device.sn,
            device.sn8,
            device.model,
        )
        self._device = device
        self._manufacturer = manufacturer
        self._rationale = rationale
        self._entity_key = entity_key
        self._config = config

    @property
    def entity_id_suffix(self) -> str:
        """Return the suffix for entity ID."""
        return f"switch_{self._entity_key}"

    @property
    def is_on(self) -> bool:
        """Return if the switch is on."""
        value = self.device_attributes.get(self._entity_key)
        if isinstance(value, bool):
            return value
        return value == 1 or value == "on" or value == "true"

    async def async_turn_on(self):
        """Turn the switch on."""
        await self.async_set_attribute(self._entity_key, True)

    async def async_turn_off(self):
        """Turn the switch off."""
        await self.async_set_attribute(self._entity_key, False)
