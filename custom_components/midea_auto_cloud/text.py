from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.TEXT,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaTextEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaTextEntity(MideaEntity, TextEntity):
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
        self._attr_native_min = config.get("min_length", 0)
        self._attr_native_max = config.get("max_length", 100)
        mode_str = config.get("mode", "text")
        self._attr_mode = getattr(TextMode, mode_str.upper(), TextMode.TEXT)
        self._attr_pattern = config.get("pattern", "^$|^[a-z][a-z0-9_]*\\.[a-z0-9_]+$")
        if "unit_of_measurement" in config:
            self._attr_native_unit_of_measurement = config["unit_of_measurement"]
        self._default = config.get("default", "")

    @property
    def native_value(self) -> str | None:
        attribute = self._config.get("attribute", self._entity_key)
        value = self._get_nested_value(attribute)
        if value is not None and isinstance(value, str):
            return value
        return self._default or None

    async def async_set_value(self, value: str) -> None:
        attribute = self._config.get("attribute", self._entity_key)
        await self.async_set_attribute(attribute, value)
