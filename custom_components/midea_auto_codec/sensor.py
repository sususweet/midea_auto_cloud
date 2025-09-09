from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    Platform,
    CONF_DEVICE_ID,
    CONF_ENTITIES, CONF_DEVICE
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
    """Set up sensor entities for Midea devices."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_data = hass.data[DOMAIN][DEVICES][device_id]
    coordinator = device_data.get("coordinator")
    device = device_data.get(CONF_DEVICE)
    manufacturer = device_data.get("manufacturer")
    rationale = device_data.get("rationale")
    entities = device_data.get(CONF_ENTITIES, {}).get(Platform.SENSOR, {})
    
    devs = []
    if entities:
        for entity_key, config in entities.items():
            devs.append(MideaSensorEntity(
                coordinator, device, manufacturer, rationale, entity_key, config
            ))
    async_add_entities(devs)


class MideaSensorEntity(MideaEntity, SensorEntity):
    """Midea sensor entity."""

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
        return f"sensor_{self._entity_key}"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.device_attributes.get(self._entity_key)
