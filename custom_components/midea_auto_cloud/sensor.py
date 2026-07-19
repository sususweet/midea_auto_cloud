from homeassistant.components.sensor import SensorEntity
from homeassistant.const import Platform, UnitOfTemperature
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
        self._key_dynamic_unit = self._config.get("dynamic_unit")
        if "suggested_display_precision" in self._config:
            self._attr_suggested_display_precision = self._config["suggested_display_precision"]
        if "options" in self._config:
            self._attr_options = self._config["options"]

    @property
    def native_unit_of_measurement(self):
        """Return the native unit (static or device attribute driven)."""
        if isinstance(self._key_dynamic_unit, str):
            raw = self._get_nested_value(self._key_dynamic_unit)
            try:
                value = int(raw)
            except (TypeError, ValueError):
                value = 0
            return UnitOfTemperature.FAHRENHEIT if value == 1 else UnitOfTemperature.CELSIUS
        return super().native_unit_of_measurement

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        if self._computed_status:
            from .device_mapping.T0xE1 import get_status_num, get_status_text
            attrs = self.device_attributes
            mapping = getattr(self.coordinator, "_device_mapping", {}) or {}
            keep_text = mapping.get("_keep_text_name", "")
            dry_text = mapping.get("_dry_text_name", "")
            keep_start_now = getattr(self.coordinator, "_keep_start_now", False)
            status_num = get_status_num(
                attrs.get("work_status"),
                airswitch=attrs.get("airswitch", 0),
                air_left_hour=attrs.get("air_left_hour", 0),
                dryswitch=attrs.get("dryswitch", 0),
                keep_start_now=keep_start_now,
            )
            return get_status_text(status_num, keep_text, dry_text)

        attribute = self._config.get("attribute", self._entity_key)
        value = self._get_nested_value(attribute)
        if isinstance(value, str) and value.lower() in ['invalid', 'none', 'null', '']:
            return None
        if isinstance(value, str):
            try:
                if '.' not in value:
                    return int(value)
                return float(value)
            except (ValueError, TypeError):
                device_class = self._config.get("device_class")
                if device_class and "enum" not in device_class.lower():
                    return None
                return value
        return value
