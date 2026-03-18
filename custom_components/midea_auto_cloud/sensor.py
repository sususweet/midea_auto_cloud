from homeassistant.components.sensor import SensorEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities for Midea devices."""
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.SENSOR,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaSensorEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


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
            entity_key,
            device=device,
            manufacturer=manufacturer,
            rationale=rationale,
            config=config,
        )

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        # Use attribute from config if available, otherwise fall back to entity_key
        attribute = self._config.get("attribute", self._entity_key)
        value = self._get_nested_value(attribute)
        
        # Handle invalid string values
        if isinstance(value, str) and value.lower() in ['invalid', 'none', 'null', '']:
            return None
            
        # Try to convert to number if it's a string that looks like a number
        if isinstance(value, str):
            try:
                # Try integer first
                if '.' not in value:
                    return int(value)
                # Then float
                return float(value)
            except (ValueError, TypeError):
                # If conversion fails, return None for numeric sensors
                # or return the original string for enum sensors
                device_class = self._config.get("device_class")
                if device_class and "enum" not in device_class.lower():
                    return None
                return value
                
        return value
