from typing import Any

from homeassistant.components.cover import CoverEntity, CoverEntityFeature, CoverState
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
        Platform.COVER,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaCoverEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaCoverEntity(MideaEntity, CoverEntity):
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
        self._open_value = config.get("open_value", "open")
        self._close_value = config.get("close_value", "close")
        self._stop_value = config.get("stop_value", "stop")
        self._position_key = config.get("position_key")

        device_class = config.get("device_class")
        if device_class:
            self._attr_device_class = device_class

        self._attr_assumed_state = True

        features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        if self._position_key:
            features |= CoverEntityFeature.SET_POSITION
        self._attr_supported_features = features

    @property
    def is_closed(self) -> bool | None:
        if self._position_key:
            position = self._get_nested_value(self._position_key)
            if position is not None:
                try:
                    return int(position) == 0
                except (ValueError, TypeError):
                    pass
        value = self._get_nested_value(self._entity_key)
        if value == self._stop_value:
            return False
        return None

    @property
    def current_cover_position(self) -> int | None:
        if self._position_key:
            position = self._get_nested_value(self._position_key)
            if position is not None:
                try:
                    return int(position)
                except (ValueError, TypeError):
                    pass
        return None

    @property
    def is_opening(self) -> bool:
        value = self._get_nested_value(self._entity_key)
        return value == self._open_value

    @property
    def is_closing(self) -> bool:
        value = self._get_nested_value(self._entity_key)
        return value == self._close_value

    @property
    def state(self) -> str | None:
        if self.is_opening:
            return CoverState.OPENING
        if self.is_closing:
            return CoverState.CLOSING
        value = self._get_nested_value(self._entity_key)
        if value == self._stop_value:
            return "stopped"
        if self.is_closed:
            return CoverState.CLOSED
        if self.is_closed is False:
            return CoverState.OPEN
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        value = self._get_nested_value(self._entity_key)
        if value == self._open_value:
            return {"motion_status": "opening"}
        if value == self._close_value:
            return {"motion_status": "closing"}
        if value == self._stop_value:
            return {"motion_status": "stopped"}
        return {"motion_status": "unknown"}

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self.async_set_attribute(self._entity_key, self._open_value)

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self.async_set_attribute(self._entity_key, self._close_value)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        await self.async_set_attribute(self._entity_key, self._stop_value)

    async def async_set_cover_position(self, position: int, **kwargs: Any) -> None:
        if self._position_key:
            await self.async_set_attribute(self._position_key, position)
