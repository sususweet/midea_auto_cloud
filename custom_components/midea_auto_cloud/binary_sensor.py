import json

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities

MAX_ATTRIBUTES_BYTES = 16000


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    def _per_device_hook(devs, coordinator, device, manufacturer, rationale, config):
        if coordinator and device:
            devs.append(
                MideaDeviceStatusSensorEntity(coordinator, device, manufacturer, rationale)
            )

    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.BINARY_SENSOR,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaBinarySensorEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
        per_device_hook=_per_device_hook,
    )


class MideaDeviceStatusSensorEntity(MideaEntity, BinarySensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "device_status"

    def __init__(self, coordinator, device, manufacturer, rationale):
        super().__init__(
            coordinator,
            device.device_id,
            device.device_name,
            f"T0x{device.device_type:02X}",
            device.sn,
            device.sn8,
            device.model,
            "device_status",
            device=device,
            manufacturer=manufacturer,
            rationale=rationale,
            config={},
        )

    @property
    def device_class(self):
        return BinarySensorDeviceClass.CONNECTIVITY

    @property
    def icon(self):
        return "mdi:devices" if self.is_on else "mdi:devices-off"

    @property
    def is_on(self):
        if self.coordinator.data:
            return self.coordinator.data.connected
        return False

    @property
    def extra_state_attributes(self) -> dict:
        attributes = {
            "device_id": str(self._device_id),
            "sn": self._sn,
            "sn8": self._sn8,
            "model": self._model,
            "device_type": self._device_type,
        }
        current_size = len(json.dumps(attributes, default=str))
        other_attrs = {}
        for key, value in self.device_attributes.items():
            if value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                other_attrs[key] = value
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_value is not None and isinstance(sub_value, (str, int, float, bool)):
                        other_attrs[f"{key}_{sub_key}"] = sub_value

        for key in sorted(other_attrs.keys()):
            pair_size = len(json.dumps({key: other_attrs[key]}, default=str))
            if current_size + pair_size > MAX_ATTRIBUTES_BYTES:
                break
            attributes[key] = other_attrs[key]
            current_size += pair_size
        return attributes


class MideaBinarySensorEntity(MideaEntity, BinarySensorEntity):
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
    def is_on(self):
        if not self.available:
            return False
        attribute = self._config.get("attribute", self._entity_key)
        value = self._get_nested_value(attribute)
        sensor_rationale = self._config.get("rationale")
        if sensor_rationale and len(sensor_rationale) == 2:
            try:
                return bool(sensor_rationale.index(value))
            except ValueError:
                pass
        if isinstance(value, bool):
            return value
        return value in (1, "1", "on", "true", "yes")
