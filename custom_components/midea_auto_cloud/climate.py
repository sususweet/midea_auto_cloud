from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    ATTR_HVAC_MODE,
)
from homeassistant.const import (
    Platform,
    ATTR_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
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
    """Set up climate entities for Midea devices."""
    # 账号型 entry：从 __init__ 写入的 accounts 桶加载设备和协调器
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
        entities_cfg = (config.get("entities") or {}).get(Platform.CLIMATE, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None

        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaClimateEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))
    async_add_entities(devs)


class MideaClimateEntity(MideaEntity, ClimateEntity):
    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        # 自动判断是否为中央空调设备（T0x21）
        self._is_central_ac = device.device_type == 0x21

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
        self._key_pre_mode = self._config.get("pre_mode")
        self._key_hvac_modes = self._config.get("hvac_modes")
        self._key_preset_modes = self._config.get("preset_modes")
        self._key_aux_heat = self._config.get("aux_heat")
        self._key_swing_modes = self._config.get("swing_modes")
        self._key_fan_modes = self._config.get("fan_modes")
        self._key_min_temp = self._config.get("min_temp")
        self._key_max_temp = self._config.get("max_temp")
        self._key_current_temperature = self._config.get("current_temperature")
        self._key_target_temperature = self._config.get("target_temperature")
        self._key_min_humidity = self._config.get("min_humidity")
        self._key_max_humidity = self._config.get("max_humidity")
        self._key_current_humidity = self._config.get("current_humidity")
        self._key_target_humidity = self._config.get("target_humidity")
        self._attr_temperature_unit = self._config.get("temperature_unit")
        self._attr_precision = self._config.get("precision")

    @property
    def supported_features(self):
        features = ClimateEntityFeature(0)
        features |= ClimateEntityFeature.TURN_ON
        features |= ClimateEntityFeature.TURN_OFF
        if self._key_target_temperature is not None:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        if self._key_target_humidity is not None:
            features |= ClimateEntityFeature.TARGET_HUMIDITY
        if self._key_preset_modes is not None:
            features |= ClimateEntityFeature.PRESET_MODE
        # if self._key_aux_heat is not None:
        #     features |= ClimateEntityFeature.AUX_HEAT
        if self._key_swing_modes is not None:
            features |= ClimateEntityFeature.SWING_MODE
        if self._key_fan_modes is not None:
            features |= ClimateEntityFeature.FAN_MODE
        return features

    @property
    def current_temperature(self):
        temp = self._get_nested_value(self._key_current_temperature)
        if temp is not None:
            try:
                return float(temp)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def target_temperature(self):
        if self._is_central_ac:
            run_mode = self._get_nested_value(self._key_power) or "0"
            if run_mode == "2":  # 制冷模式
                return self._get_nested_value("cool_temp_set")
            elif run_mode == "3":  # 制热模式
                return self._get_nested_value("cool_temp_set")
            return None
        else:
            if isinstance(self._key_target_temperature, list):
                temp_int = self._get_nested_value(self._key_target_temperature[0])
                tem_dec = self._get_nested_value(self._key_target_temperature[1])
                if temp_int is not None and tem_dec is not None:
                    try:
                        return float(temp_int) + float(tem_dec)
                    except (ValueError, TypeError):
                        return None
                return None
            else:
                temp = self._get_nested_value(self._key_target_temperature)
                if temp is not None:
                    try:
                        return float(temp)
                    except (ValueError, TypeError):
                        return None
                return None

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity."""
        humidity = self._get_nested_value(self._key_current_humidity)
        if humidity is not None:
            try:
                return float(humidity)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def target_humidity(self) -> float | None:
        """Return the humidity we try to reach."""
        humidity = self._get_nested_value(self._key_target_humidity)
        if humidity is not None:
            try:
                return float(humidity)
            except (ValueError, TypeError):
                return None
        return None

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
    def min_humidity(self):
        if isinstance(self._key_min_humidity, str):
            return float(self.device_attributes.get(self._key_min_humidity, 45))
        else:
            return float(self._key_min_humidity)

    @property
    def max_humidity(self):
        if isinstance(self._key_max_humidity, str):
            return float(self.device_attributes.get(self._key_max_humidity, 65))
        else:
            return float(self._key_max_humidity)

    @property
    def target_temperature_low(self):
        return self.min_temp

    @property
    def target_temperature_high(self):
        return self.max_temp

    @property
    def target_humidity_low(self):
        return self.min_humidity

    @property
    def target_humidity_high(self):
        return self.max_humidity

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
        return self._dict_get_selected(self._key_fan_modes)

    @property
    def swing_modes(self):
        if self._is_central_ac:
            return ["off", "on"]
        else:
            return list(self._key_swing_modes.keys())

    @property
    def swing_mode(self):
        if self._is_central_ac:
            extflag = self._get_nested_value("extflag") or "0"
            # extflag: 4=摇摆, 6=电辅热+摇摆
            if extflag in ["4", "6"]:
                return "on"
            return "off"
        else:
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

    async def async_toggle(self):
        if self.is_on:
            await self.async_turn_off()
        else:
            await self.async_turn_on()

    async def async_set_temperature(self, **kwargs):
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = kwargs.get(ATTR_TEMPERATURE)
        
        if self._is_central_ac:
            run_mode = self._get_nested_value(self._key_power) or "0"
            control = {}
            
            if run_mode == "2":  # 制冷模式
                control["cooling_temp"] = str(temperature)
            elif run_mode == "3":  # 制热模式
                control["cooling_temp"] = str(temperature)
                control["heating_temp"] = str(temperature)
            
            if control:
                await self.coordinator.async_send_central_ac_control(control)
        else:
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

    async def async_set_humidity(self, humidity: int):
        if self._key_target_humidity is None:
            return
        new_status = {}
        new_status[self._key_target_humidity] = int(humidity)
        await self.async_set_attributes(new_status)

    async def async_set_fan_mode(self, fan_mode: str):
        if self._is_central_ac:
            fan_speed = self._key_fan_modes.get(fan_mode)
            await self.coordinator.async_send_central_ac_control(fan_speed)
        else:
            new_status = self._key_fan_modes.get(fan_mode)
            await self.async_set_attributes(new_status)

    async def async_set_preset_mode(self, preset_mode: str):
        if self._is_central_ac:
            new_status = self._key_preset_modes.get(preset_mode)
            await self.coordinator.async_send_central_ac_control(new_status)
        else:
            new_status = self._key_preset_modes.get(preset_mode)
            await self.async_set_attributes(new_status)

    async def async_set_hvac_mode(self, hvac_mode: str):
        if self._is_central_ac:
            run_mode = self._key_hvac_modes.get(hvac_mode)
            await self.coordinator.async_send_central_ac_control(run_mode)
        else:
            new_status = self._key_hvac_modes.get(hvac_mode)
            await self.async_set_attributes(new_status)

    async def async_set_swing_mode(self, swing_mode: str):
        if self._is_central_ac:
            current_extflag = self._get_nested_value("extflag") or "0"
            
            if swing_mode == "on":
                # 开启摆风：如果当前有电辅热(2)，则设为6(电辅热+摆风)，否则设为4(摆风)
                if current_extflag == "2":
                    new_extflag = "6"  # 电辅热+摆风
                else:
                    new_extflag = "4"  # 仅摆风
            else:
                # 关闭摆风：如果当前是6(电辅热+摆风)，则设为2(仅电辅热)，否则设为0(关闭)
                if current_extflag == "6":
                    new_extflag = "2"  # 仅电辅热
                else:
                    new_extflag = "0"  # 关闭
            
            control = {"extflag": new_extflag}
            await self.coordinator.async_send_central_ac_control(control)
        else:
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
        value = self._get_nested_value(key)
        if isinstance(value, bool):
            return value
        return value == 1 or value == "on" or value == "true"

    async def _async_set_status_on_off(self, attribute_key: str | None, turn_on: bool):
        """Set on/off status for device attribute."""
        if attribute_key is None:
            return
        new_status = {}
        new_status[attribute_key] = self._rationale[int(turn_on)]
        if turn_on:
            new_status[self._key_pre_mode] = self._get_nested_value(self._key_pre_mode)
        await self.async_set_attributes(new_status)
