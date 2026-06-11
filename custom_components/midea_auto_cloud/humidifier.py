from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierDeviceClass,
    HumidifierEntityFeature,
    HumidifierAction,
)
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
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.HUMIDIFIER,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaHumidifierEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaHumidifierEntity(MideaEntity, HumidifierEntity):
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
        self._key_power = self._config.get("power")
        self._key_target_humidity = self._config.get("target_humidity")
        self._key_current_humidity = self._config.get("current_humidity")
        self._key_external_humidity = "external_humidity_sensor"
        self._key_mode = self._config.get("mode")
        self._key_modes = self._config.get("modes") or {}
        self._min_humidity = self._config.get("min_humidity", 30)
        self._max_humidity = self._config.get("max_humidity", 80)
        self._target_humidity_step = self._config.get("target_humidity_step", 1)

        if self._key_modes:
            self._attr_supported_features = HumidifierEntityFeature.MODES

        external_map = self._config.get("external_humidity_sensor_map", {})
        self._external_sensor_by_sn8 = external_map.get(self._sn8) if external_map else None

    @property
    def device_class(self):
        return self._config.get("device_class", HumidifierDeviceClass.HUMIDIFIER)

    @property
    def min_humidity(self) -> int:
        return self._min_humidity

    @property
    def max_humidity(self) -> int:
        return self._max_humidity

    @property
    def target_humidity_step(self) -> int | float | None:
        return self._target_humidity_step

    @property
    def action(self) -> HumidifierAction:
        if not self.is_on:
            return HumidifierAction.OFF
        current = self.current_humidity
        target = self.target_humidity
        if current is None or target is None:
            return HumidifierAction.IDLE
        dc = self.device_class
        if dc == HumidifierDeviceClass.DEHUMIDIFIER and current > target:
            return HumidifierAction.DRYING
        if dc == HumidifierDeviceClass.HUMIDIFIER and current < target:
            return HumidifierAction.HUMIDIFYING
        return HumidifierAction.IDLE

    @property
    def is_on(self) -> bool:
        if not self._key_power:
            return False
        return self._get_status_on_off(self._key_power)

    @property
    def target_humidity(self) -> int | None:
        if not self._key_target_humidity:
            return None
        value = self._get_nested_value(self._key_target_humidity)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @property
    def current_humidity(self) -> int | None:
        external_entity_id = self._external_sensor_by_sn8
        if not external_entity_id:
            external_entity_id = self._get_nested_value(self._key_external_humidity)
        if external_entity_id and isinstance(external_entity_id, str) and external_entity_id.strip():
            state = self.hass.states.get(external_entity_id.strip())
            if state and state.state not in ("unknown", "unavailable", None):
                try:
                    return int(float(state.state))
                except (ValueError, TypeError):
                    pass
            return None
        if not self._key_current_humidity:
            return None
        value = self._get_nested_value(self._key_current_humidity)
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    @property
    def mode(self) -> str | None:
        if not self._key_mode:
            return None
        return self._get_nested_value(self._key_mode)

    @property
    def available_modes(self) -> list[str] | None:
        if self._key_modes:
            return list(self._key_modes.keys())
        return None

    async def async_turn_on(self, **kwargs) -> None:
        if self._key_power:
            await self._async_set_status_on_off(self._key_power, True)

    async def async_turn_off(self, **kwargs) -> None:
        if self._key_power:
            await self._async_set_status_on_off(self._key_power, False)

    async def async_set_humidity(self, humidity: int) -> None:
        if self._key_target_humidity:
            await self.async_set_attribute(self._key_target_humidity, humidity)

    async def async_set_mode(self, mode: str) -> None:
        if not self._key_modes or mode not in self._key_modes:
            return
        mode_config = self._key_modes[mode]
        if isinstance(mode_config, dict):
            await self.async_set_attributes(mode_config)
        elif self._key_mode:
            await self.async_set_attribute(self._key_mode, mode)
