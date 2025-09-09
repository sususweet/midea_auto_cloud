from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    ATTR_HVAC_MODE,
)
from homeassistant.const import (
    Platform,
    CONF_DEVICE_ID,
    CONF_ENTITIES,
    ATTR_TEMPERATURE, CONF_DEVICE
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    DEVICES
)
from .midea_entity import MideaEntity
from .midea_entities import Rationale


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate entities for Midea devices."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_data = hass.data[DOMAIN][DEVICES][device_id]
    coordinator = device_data.get("coordinator")
    device = device_data.get(CONF_DEVICE)
    manufacturer = device_data.get("manufacturer")
    rationale = device_data.get("rationale")
    entities = device_data.get(CONF_ENTITIES, {}).get(Platform.CLIMATE, {})
    
    devs = []
    if entities:
        for entity_key, config in entities.items():
            devs.append(MideaClimateEntity(
                coordinator, device, manufacturer, rationale, entity_key, config
            ))
    async_add_entities(devs)


class MideaClimateEntity(MideaEntity, ClimateEntity):
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
        self._key_power = self._config.get("power")
        self._key_hvac_modes = self._config.get("hvac_modes")
        self._key_preset_modes = self._config.get("preset_modes")
        self._key_aux_heat = self._config.get("aux_heat")
        self._key_swing_modes = self._config.get("swing_modes")
        self._key_fan_modes = self._config.get("fan_modes")
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
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        if self._key_preset_modes is not None:
            features |= ClimateEntityFeature.PRESET_MODE
        if self._key_aux_heat is not None:
            features |= ClimateEntityFeature.AUX_HEAT
        if self._key_swing_modes is not None:
            features |= ClimateEntityFeature.SWING_MODE
        if self._key_fan_modes is not None:
            features |= ClimateEntityFeature.FAN_MODE
        return features

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
            return float(self.device_attributes.get(self._key_min_temp, 16))
        else:
            return float(self._key_min_temp)

    @property
    def max_temp(self):
        if isinstance(self._key_max_temp, str):
            return float(self.device_attributes.get(self._key_max_temp, 30))
        else:
            return float(self._key_max_temp)

    @property
    def target_temperature_low(self):
        return self.min_temp

    @property
    def target_temperature_high(self):
        return self.max_temp

    @property
    def preset_modes(self):
        return list(self._key_preset_modes.keys())

    @property
    def preset_mode(self):
        return self._dict_get_selected(self._key_preset_modes)

    @property
    def fan_modes(self):
        return list(self._key_fan_modes.keys())

    @property
    def fan_mode(self):
        return self._dict_get_selected(self._key_fan_modes, Rationale.LESS)

    @property
    def swing_modes(self):
        return list(self._key_swing_modes.keys())

    @property
    def swing_mode(self):
        return self._dict_get_selected(self._key_swing_modes)

    @property
    def is_on(self) -> bool:
        return self.hvac_mode != HVACMode.OFF

    @property
    def hvac_mode(self):
        return self._dict_get_selected(self._key_hvac_modes)

    @property
    def hvac_modes(self):
        return list(self._key_hvac_modes.keys())

    @property
    def is_aux_heat(self):
        return self._get_status_on_off(self._key_aux_heat)

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
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode is not None:
            new_status = self._key_hvac_modes.get(hvac_mode)
        else:
            new_status = {}
        if isinstance(self._key_target_temperature, list):
            new_status[self._key_target_temperature[0]] = temp_int
            new_status[self._key_target_temperature[1]] = temp_dec
        else:
            new_status[self._key_target_temperature] = temperature
        await self.async_set_attributes(new_status)

    async def async_set_fan_mode(self, fan_mode: str):
        new_status = self._key_fan_modes.get(fan_mode)
        await self.async_set_attributes(new_status)

    async def async_set_preset_mode(self, preset_mode: str):
        new_status = self._key_preset_modes.get(preset_mode)
        await self.async_set_attributes(new_status)

    async def async_set_hvac_mode(self, hvac_mode: str):
        new_status = self._key_hvac_modes.get(hvac_mode)
        await self.async_set_attributes(new_status)

    async def async_set_swing_mode(self, swing_mode: str):
        new_status = self._key_swing_modes.get(swing_mode)
        await self.async_set_attributes(new_status)

    async def async_turn_aux_heat_on(self) -> None:
        await self._async_set_status_on_off(self._key_aux_heat, True)

    async def async_turn_aux_heat_off(self) -> None:
        await self._async_set_status_on_off(self._key_aux_heat, False)

    def _get_status_on_off(self, key):
        """Get on/off status from device attributes."""
        if key is None:
            return False
        value = self.device_attributes.get(key)
        if isinstance(value, bool):
            return value
        return value == 1 or value == "on" or value == "true"

    async def _async_set_status_on_off(self, key, value):
        """Set on/off status for device attribute."""
        if key is None:
            return
        await self.async_set_attribute(key, value)

    def _dict_get_selected(self, dict_config, rationale=Rationale.EQUAL):
        """Get selected value from dictionary configuration."""
        if dict_config is None:
            return None
        
        for key, config in dict_config.items():
            if isinstance(config, dict):
                # Check if all conditions match
                match = True
                for attr_key, attr_value in config.items():
                    device_value = self.device_attributes.get(attr_key)
                    if rationale == Rationale.EQUAL:
                        if device_value != attr_value:
                            match = False
                            break
                    elif rationale == Rationale.LESS:
                        if device_value >= attr_value:
                            match = False
                            break
                    elif rationale == Rationale.GREATER:
                        if device_value <= attr_value:
                            match = False
                            break
                if match:
                    return key
        return None
