from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    Platform,
    ATTR_TEMPERATURE
)
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
    """Set up water heater entities for Midea devices."""
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
        entities_cfg = (config.get("entities") or {}).get(Platform.WATER_HEATER, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaWaterHeaterEntityEntity(coordinator, device, manufacturer, rationale, entity_key, ecfg))
    async_add_entities(devs)


class MideaWaterHeaterEntityEntity(MideaEntity, WaterHeaterEntity):
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
        self._device = device
        self._manufacturer = manufacturer
        self._rationale = rationale
        self._config = config
        self._key_power = self._config.get("power")
        self._key_operation_list = self._config.get("operation_list")
        self._key_min_temp = self._config.get("min_temp")
        self._key_max_temp = self._config.get("max_temp")
        self._key_current_temperature = self._config.get("current_temperature")
        self._key_target_temperature = self._config.get("target_temperature")
        self._attr_temperature_unit = self._config.get("temperature_unit")
        self._attr_precision = self._config.get("precision")

    @property
    def supported_features(self):
        features = 0
        if self._key_target_temperature is not None:
            features |= WaterHeaterEntityFeature.TARGET_TEMPERATURE
        if self._key_operation_list is not None:
            features |= WaterHeaterEntityFeature.OPERATION_MODE
        return features

    @property
    def operation_list(self):
        return list(self._key_operation_list.keys())

    @property
    def current_operation(self):
        return self._dict_get_selected(self._key_operation_list)

    @property
    def current_temperature(self):
        return self.device_attributes.get(self._key_current_temperature)

    @property
    def target_temperature(self):
        if isinstance(self._key_target_temperature, list):
            temp_int = self.device_attributes.get(self._key_target_temperature[0])
            tem_dec = self.device_attributes.get(self._key_target_temperature[1])
            if temp_int is not None and tem_dec is not None:
                return temp_int + tem_dec
            return None
        else:
            return self.device_attributes.get(self._key_target_temperature)

    @property
    def min_temp(self):
        if isinstance(self._key_min_temp, str):
            return float(self.device_attributes.get(self._key_min_temp))
        else:
            return float(self._key_min_temp)

    @property
    def max_temp(self):
        if isinstance(self._key_max_temp, str):
            return float(self.device_attributes.get(self._key_max_temp))
        else:
            return float(self._key_max_temp)

    @property
    def target_temperature_low(self):
        return self.min_temp

    @property
    def target_temperature_high(self):
        return self.max_temp

    @property
    def is_on(self) -> bool:
        return self._get_status_on_off(self._key_power)

    async def async_turn_on(self):
        await self._async_set_status_on_off(self._key_power, True)

    async def async_turn_off(self):
        await self._async_set_status_on_off(self._key_power, False)

    async def async_set_temperature(self, **kwargs):
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = kwargs.get(ATTR_TEMPERATURE)
        temp_int, temp_dec = divmod(temperature, 1)
        temp_int = int(temp_int)
        new_status = {}
        if isinstance(self._key_target_temperature, list):
            new_status[self._key_target_temperature[0]] = temp_int
            new_status[self._key_target_temperature[1]] = temp_dec
        else:
            new_status[self._key_target_temperature] = temperature
        await self.async_set_attributes(new_status)

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        new_status = self._key_operation_list.get(operation_mode)
        if new_status:
            await self.async_set_attributes(new_status)

