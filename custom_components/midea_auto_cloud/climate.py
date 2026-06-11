from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_LOW,
    ATTR_TARGET_TEMP_HIGH,
)
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.const import (
    Platform,
    ATTR_TEMPERATURE,
    UnitOfTemperature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    FAN_ONLY_ENTITY_KEY,
    MANUAL_FAN_MODE_ORDER,
    NUMERIC_FAN_MODE_DISPLAY_ORDER,
    build_fan_only_fan_mode_configs,
    default_manual_fan_mode,
    fan_mode_lookup_mapping,
    is_numeric_six_key_fan_mode_mapping,
    normalize_fan_mode_input,
    supports_fan_only_derived_fan,
)
from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate entities for Midea devices."""
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.CLIMATE,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaClimateEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


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
        # Optional dual-setpoint range (e.g. T0x44 in auto mode). When the current
        # hvac mode is listed in range_hvac_modes, the entity exposes a low/high
        # range and writes these attributes instead of the single setpoint.
        self._key_target_temperature_low = self._config.get("target_temperature_low")
        self._key_target_temperature_high = self._config.get("target_temperature_high")
        self._range_hvac_modes = self._config.get("range_hvac_modes") or []
        # Optional runtime-status attributes for hvac_action: which device
        # attribute reports the compressor / indoor-fan run state, and the
        # auto-resolved cooling/heating direction.
        self._key_action_compressor = self._config.get("action_compressor")
        self._key_action_fan = self._config.get("action_fan")
        self._key_action_direction = self._config.get("action_direction")
        self._key_min_humidity = self._config.get("min_humidity")
        self._key_max_humidity = self._config.get("max_humidity")
        self._key_current_humidity = self._config.get("current_humidity")
        self._key_target_humidity = self._config.get("target_humidity")
        self._key_temperature_unit = self._config.get("temperature_unit")
        self._device_type = device.device_type
        self._attr_temperature_unit = (
            self._key_temperature_unit
            if not isinstance(self._key_temperature_unit, str)
            else UnitOfTemperature.CELSIUS
        )
        self._attr_precision = self._config.get("precision")
        self._attr_target_temperature_step = self._config.get("precision")

    @property
    def is_bath_heater(self) -> bool:
        return self._device_type == 0x26

    @staticmethod
    def _safe_convert_to_float(value) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @property
    def temperature_unit(self):
        """Return the temperature unit (static or device attribute driven).

        If mapping provides a string key (e.g. "temperature_unit"), it is read from device attributes:
        - 1 => Fahrenheit
        - 0/others => Celsius
        """
        if isinstance(self._key_temperature_unit, str):
            raw = self._get_nested_value(self._key_temperature_unit)
            try:
                value = int(raw)
            except (TypeError, ValueError):
                value = 0
            return UnitOfTemperature.FAHRENHEIT if value == 1 else UnitOfTemperature.CELSIUS
        return self._attr_temperature_unit

    def _uses_temperature_range(self) -> bool:
        """The current hvac mode controls a low/high range, not a single setpoint."""
        return (
            self._key_target_temperature_low is not None
            and self._key_target_temperature_high is not None
            and self.hvac_mode in self._range_hvac_modes
        )

    @property
    def supported_features(self):
        features = ClimateEntityFeature(0)
        features |= ClimateEntityFeature.TURN_ON
        features |= ClimateEntityFeature.TURN_OFF
        if self._uses_temperature_range():
            features |= ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        elif self._key_target_temperature is not None:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        if self._key_target_humidity is not None:
            features |= ClimateEntityFeature.TARGET_HUMIDITY
        if self._key_preset_modes is not None:
            features |= ClimateEntityFeature.PRESET_MODE
        if self._key_aux_heat is not None and hasattr(ClimateEntityFeature, "AUX_HEAT"):
            features |= ClimateEntityFeature.AUX_HEAT
        if self._key_swing_modes is not None:
            features |= ClimateEntityFeature.SWING_MODE
        if self._key_fan_modes is not None:
            features |= ClimateEntityFeature.FAN_MODE
        return features

    @property
    def current_temperature(self):
        if isinstance(self._key_current_temperature, list):
            temp_int = self._get_nested_value(self._key_current_temperature[0])
            tem_dec = self._get_nested_value(self._key_current_temperature[1])
            if temp_int is not None and tem_dec is not None:
                t_int = self._safe_convert_to_float(temp_int)
                t_dec = self._safe_convert_to_float(tem_dec)
                if t_int is not None and t_dec is not None:
                    return t_int + t_dec
            return None
        return self._safe_convert_to_float(
            self._get_nested_value(self._key_current_temperature)
        )

    def _get_bath_heater_hvac_mode(self) -> HVACMode:
        current_mode = self._get_nested_value("mode")
        if current_mode == "close_all":
            return HVACMode.OFF
        mode_mapping = {
            "heating": HVACMode.HEAT,
            "bath": HVACMode.HEAT,
            "drying": HVACMode.DRY,
            "ventilation": HVACMode.AUTO,
            "blowing": HVACMode.FAN_ONLY,
        }
        return mode_mapping.get(current_mode, HVACMode.AUTO)

    def _get_bath_heater_target_temp(self) -> float | None:
        if not isinstance(self._key_target_temperature, dict):
            return None
        current_mode = self.preset_mode
        key = self._key_target_temperature.get(current_mode)
        if not key:
            return None
        return self._safe_convert_to_float(self._get_nested_value(key))

    def _get_target_temp_from_list(self) -> float | None:
        if len(self._key_target_temperature) == 1:
            return self._safe_convert_to_float(
                self._get_nested_value(self._key_target_temperature[0])
            )
        temp_int = self._get_nested_value(self._key_target_temperature[0])
        tem_dec = self._get_nested_value(self._key_target_temperature[1])
        if temp_int is not None and tem_dec is not None:
            t_int = self._safe_convert_to_float(temp_int)
            t_dec = self._safe_convert_to_float(tem_dec)
            if t_int is not None and t_dec is not None:
                return t_int + t_dec
        return None

    def _match_swing_option(self, options: dict, current_value: str) -> str | None:
        for option_key, option_config in options.items():
            if isinstance(option_config, dict):
                if any(str(attr_value) == current_value for attr_value in option_config.values()):
                    return option_key
            elif str(option_config) == current_value:
                return option_key
        return None

    def _get_bath_heater_swing_mode(self) -> str | None:
        current_mode = self.preset_mode
        mode_config = self._key_swing_modes.get(current_mode)
        if not (mode_config and isinstance(mode_config, dict)):
            return self._dict_get_selected(self._key_swing_modes)
        direction_key = mode_config.get("key")
        options = mode_config.get("options")
        if not (direction_key and options):
            return self._dict_get_selected(self._key_swing_modes)
        current_value = self._get_nested_value(direction_key)
        if current_value is None:
            return None
        return self._match_swing_option(options, str(current_value))

    @property
    def target_temperature(self):
        if self._uses_temperature_range():
            return None
        if self._is_central_ac:
            run_mode = self._get_nested_value(self._key_power) or "0"
            if run_mode == "2":  # 制冷模式
                return self._get_nested_value("cool_temp_set")
            elif run_mode == "3":  # 制热模式
                return self._get_nested_value("cool_temp_set")
            return None
        if isinstance(self._key_target_temperature, dict):
            if self.is_bath_heater:
                return self._get_bath_heater_target_temp()
            return None
        if isinstance(self._key_target_temperature, list):
            return self._get_target_temp_from_list()
        return self._safe_convert_to_float(
            self._get_nested_value(self._key_target_temperature)
        )

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
            min_temp = self.device_attributes.get(self._key_min_temp, 16)
            return float(min_temp) if min_temp is not None else 16.0
        else:
            return float(self._key_min_temp)

    @property
    def max_temp(self):
        if isinstance(self._key_max_temp, str):
            max_temp = self.device_attributes.get(self._key_max_temp, 30)
            return float(max_temp) if max_temp is not None else 30.0
        else:
            return float(self._key_max_temp)

    @property
    def min_humidity(self):
        if isinstance(self._key_min_humidity, str):
            min_humidity = self.device_attributes.get(self._key_min_humidity, 45)
            return float(min_humidity) if min_humidity is not None else 45.0
        else:
            return float(self._key_min_humidity)

    @property
    def max_humidity(self):
        if isinstance(self._key_max_humidity, str):
            max_humidity = self.device_attributes.get(self._key_max_humidity, 65)
            return float(max_humidity) if max_humidity is not None else 65.0
        else:
            return float(self._key_max_humidity)

    @property
    def target_temperature_low(self):
        if self._uses_temperature_range():
            value = self._get_nested_value(self._key_target_temperature_low)
            if value is not None:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            return None
        return self.min_temp

    @property
    def target_temperature_high(self):
        if self._uses_temperature_range():
            value = self._get_nested_value(self._key_target_temperature_high)
            if value is not None:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            return None
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
        if is_numeric_six_key_fan_mode_mapping(self._key_fan_modes):
            return NUMERIC_FAN_MODE_DISPLAY_ORDER
        return list(self._key_fan_modes.keys())

    @property
    def fan_mode(self):
        if is_numeric_six_key_fan_mode_mapping(self._key_fan_modes):
            selected = self._dict_get_selected(fan_mode_lookup_mapping(self._key_fan_modes))
            return selected
        return self._dict_get_selected(self._key_fan_modes)

    @property
    def swing_modes(self):
        if self._is_central_ac:
            return ["off", "on"]
        if self.is_bath_heater and isinstance(self._key_swing_modes, dict):
            current_mode = self.preset_mode
            mode_config = self._key_swing_modes.get(current_mode)
            if mode_config and isinstance(mode_config, dict) and "options" in mode_config:
                return list(mode_config["options"].keys())
        return list(self._key_swing_modes.keys())

    @property
    def swing_mode(self):
        if self._is_central_ac:
            extflag = self._get_nested_value("extflag") or "0"
            # extflag: 4=摇摆, 6=电辅热+摇摆
            if extflag in ["4", "6"]:
                return "on"
            return "off"
        if self.is_bath_heater and isinstance(self._key_swing_modes, dict):
            return self._get_bath_heater_swing_mode()
        return self._dict_get_selected(self._key_swing_modes)

    @property
    def is_on(self) -> bool:
        return self.hvac_mode != HVACMode.OFF

    @property
    def hvac_mode(self):
        if self.is_bath_heater and self._key_hvac_modes is not None:
            return self._get_bath_heater_hvac_mode()
        mode = self._dict_get_selected(self._key_hvac_modes)
        return mode if mode is not None else HVACMode.OFF

    @property
    def hvac_modes(self):
        return list(self._key_hvac_modes.keys())

    @staticmethod
    def _is_running(value) -> bool:
        return value in (1, "1", True, "on", "true")

    def _running_direction(self) -> "HVACAction":
        """Cooling vs heating while the compressor is running.

        Explicit cool/heat modes are unambiguous. For auto/range mode we read the
        device's resolved direction from action_direction
        (auto_mode_actual_operating_status): 1 = cooling, 2 = heating — confirmed
        empirically on the T0x44 (cooling and idle reported 1; a real heating
        cycle reported 2, cross-checked against the Midea app). Falls back to
        room-vs-band if that value is missing or unexpected, so other variants
        degrade gracefully instead of misreporting.
        """
        mode = self.hvac_mode
        if mode == HVACMode.HEAT:
            return HVACAction.HEATING
        if mode == HVACMode.COOL:
            return HVACAction.COOLING
        if self._key_action_direction is not None:
            d = self._get_nested_value(self._key_action_direction)
            if d in (1, "1"):
                return HVACAction.COOLING
            if d in (2, "2"):
                return HVACAction.HEATING
        cur = self.current_temperature
        if cur is not None and self._uses_temperature_range():
            hi = self.target_temperature_high
            lo = self.target_temperature_low
            if lo is not None and cur <= lo:
                return HVACAction.HEATING
            if hi is not None and cur >= hi:
                return HVACAction.COOLING
        return HVACAction.COOLING

    @property
    def hvac_action(self):
        """What the equipment is actually doing (running vs idle)."""
        if not self.is_on:
            return HVACAction.OFF

        current_mode = self.hvac_mode
        if current_mode == HVACMode.FAN_ONLY:
            return HVACAction.FAN
        elif current_mode == HVACMode.DRY:
            return HVACAction.DRYING

        if (self._key_action_compressor is None and self._key_action_fan is None
                and self._key_action_direction is None):
            # Get current and target temperatures
            current_temp = self.current_temperature
            target_temp = self.target_temperature

            # If we have both temperatures, use them to determine action
            if current_temp is not None and target_temp is not None:
                if current_mode == HVACMode.HEAT:
                    # Heating if current temp is below target
                    if current_temp < target_temp:
                        return HVACAction.HEATING
                    else:
                        return HVACAction.IDLE
                elif current_mode == HVACMode.COOL:
                    # Cooling if current temp is above target
                    if current_temp > target_temp:
                        return HVACAction.COOLING
                    else:
                        return HVACAction.IDLE
                elif current_mode == HVACMode.AUTO:
                    # In auto mode, determine based on temperature difference
                    # Assuming a small hysteresis of 1 degree
                    if current_temp < target_temp - 0.5:
                        return HVACAction.HEATING
                    elif current_temp > target_temp + 0.5:
                        return HVACAction.COOLING
                    else:
                        return HVACAction.IDLE

            # Fallback to mode-based determination if temperature data is unavailable
            if current_mode == HVACMode.HEAT:
                return HVACAction.HEATING
            elif current_mode == HVACMode.COOL:
                return HVACAction.COOLING
            else:
                return HVACAction.IDLE
        else:
            """
            Only active when the mapping provides the run-status / direction keys, so
            other device types are unaffected (returns None). Running vs idle comes
            from the compressor/fan run-status flags; cooling vs heating from
            _running_direction:
              off -> OFF; compressor running -> COOLING/HEATING; only fan -> FAN;
              otherwise -> IDLE.
            """
            compressor = (
                self._is_running(self._get_nested_value(self._key_action_compressor))
                if self._key_action_compressor else False
            )
            fan = (
                self._is_running(self._get_nested_value(self._key_action_fan))
                if self._key_action_fan else False
            )
            if compressor:
                return self._running_direction()
            if fan:
                return HVACAction.FAN
            return HVACAction.IDLE

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
        if self._is_central_ac:
            if ATTR_TEMPERATURE not in kwargs:
                return
            temperature = kwargs.get(ATTR_TEMPERATURE)
            run_mode = self._get_nested_value(self._key_power) or "0"
            control = {}

            if run_mode == "2":  # 制冷模式
                control["cooling_temp"] = str(temperature)
            elif run_mode == "3":  # 制热模式
                control["cooling_temp"] = str(temperature)
                control["heating_temp"] = str(temperature)

            if control:
                await self.coordinator.async_send_central_ac_control(control)
            return

        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode is not None:
            await self.async_set_hvac_mode(hvac_mode)

        # Dual-setpoint range (e.g. T0x44 in auto mode): write the low/high limit
        # attributes instead of the single setpoint. Sent as str(int(...)) to match
        # how the corresponding number entities write these same attributes.
        target_low = kwargs.get(ATTR_TARGET_TEMP_LOW)
        target_high = kwargs.get(ATTR_TARGET_TEMP_HIGH)
        if (
            (target_low is not None or target_high is not None)
            and self._key_target_temperature_low is not None
            and self._key_target_temperature_high is not None
        ):
            new_status = {}
            if target_low is not None:
                new_status[self._key_target_temperature_low] = str(int(target_low))
            if target_high is not None:
                new_status[self._key_target_temperature_high] = str(int(target_high))
            await self.async_set_attributes(new_status)
            return

        # Single setpoint.
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if isinstance(self._key_target_temperature, dict):
            if self.is_bath_heater:
                current_mode = self.preset_mode
                target_key = self._key_target_temperature.get(current_mode)
                if target_key:
                    await self.async_set_attribute(target_key, int(temperature))
            return

        temp_int, temp_dec = divmod(temperature, 1)
        temp_int = int(temp_int)
        if hvac_mode is not None:
            new_status = self._key_hvac_modes.get(hvac_mode) or {}
        else:
            new_status = {}
        if isinstance(self._key_target_temperature, list):
            if len(self._key_target_temperature) == 2:
                new_status[self._key_target_temperature[0]] = temp_int
                new_status[self._key_target_temperature[1]] = temp_dec
            else:
                new_status[self._key_target_temperature[0]] = int(temperature)
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
        fan_mode = normalize_fan_mode_input(self._key_fan_modes, fan_mode)
        fan_modes = fan_mode_lookup_mapping(self._key_fan_modes)
        if self._is_central_ac:
            fan_speed = fan_modes.get(fan_mode)
            await self.coordinator.async_send_central_ac_control(fan_speed)
        else:
            new_status = fan_modes.get(fan_mode)
            await self.async_set_attributes(new_status)

    async def async_set_preset_mode(self, preset_mode: str):
        if self._is_central_ac:
            new_status = self._key_preset_modes.get(preset_mode)
            await self.coordinator.async_send_central_ac_control(new_status)
        else:
            new_status = self._key_preset_modes.get(preset_mode)
            await self.async_set_attributes(new_status)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        if self._is_central_ac:
            run_mode = self._key_hvac_modes.get(hvac_mode)
            await self.coordinator.async_send_central_ac_control(run_mode)
        elif self.is_bath_heater and hvac_mode != HVACMode.OFF:
            return
        else:
            new_status = self._key_hvac_modes.get(hvac_mode)
            if new_status:
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
        elif self.is_bath_heater and isinstance(self._key_swing_modes, dict):
            current_mode = self.preset_mode
            mode_config = self._key_swing_modes.get(current_mode)
            if mode_config and isinstance(mode_config, dict):
                options = mode_config.get("options") or {}
                swing_config = options.get(swing_mode)
                if swing_config:
                    await self.async_set_attributes(swing_config)
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


def _add_fan_only_derived_fan(entities, coordinator, device, manufacturer, rationale, config):
    """Add a fan-only derived fan entity if the device supports it."""
    if coordinator is None or device is None:
        return
    if not supports_fan_only_derived_fan(config):
        return
    entities.append(
        MideaFanOnlyFanEntity(
            coordinator, device, manufacturer, rationale,
            FAN_ONLY_ENTITY_KEY, config,
        )
    )


class MideaFanOnlyFanEntity(MideaEntity, FanEntity):
    """Fan-only derived entity for ACs that support hvac_mode=fan_only."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        climate_entities = (config.get("entities") or {}).get(Platform.CLIMATE, {}) or {}
        climate_config = next(
            ecfg for ecfg in climate_entities.values()
            if build_fan_only_fan_mode_configs(ecfg.get("fan_modes")).get("auto") is not None
            and any(
                mode in build_fan_only_fan_mode_configs(ecfg.get("fan_modes"))
                for mode in MANUAL_FAN_MODE_ORDER
            )
            and "fan_only" in (ecfg.get("hvac_modes") or {})
            and "off" in (ecfg.get("hvac_modes") or {})
        )
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
            config={
                "translation_key": "fan_only_fan",
            },
        )
        self._key_hvac_modes = climate_config.get("hvac_modes")
        self._fan_mode_configs = build_fan_only_fan_mode_configs(climate_config.get("fan_modes"))
        self._manual_fan_modes = [
            mode for mode in MANUAL_FAN_MODE_ORDER if mode in self._fan_mode_configs
        ]
        self._attr_speed_count = len(self._manual_fan_modes)

    @property
    def supported_features(self):
        return (
            FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
            | FanEntityFeature.SET_SPEED
            | FanEntityFeature.PRESET_MODE
        )

    @property
    def is_on(self) -> bool:
        return self._current_hvac_mode() == "fan_only"

    @property
    def preset_modes(self):
        return ["auto"]

    @property
    def preset_mode(self):
        if not self.is_on:
            return None
        if self._current_fan_mode() == "auto":
            return "auto"
        return None

    @property
    def percentage(self):
        if not self.is_on:
            return 0
        current_fan_mode = self._current_fan_mode()
        if current_fan_mode not in self._manual_fan_modes:
            return 0
        return round(
            (self._manual_fan_modes.index(current_fan_mode) + 1)
            * 100
            / len(self._manual_fan_modes)
        )

    async def async_turn_on(
            self,
            percentage: int | None = None,
            preset_mode: str | None = None,
            **kwargs,
    ):
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
            return
        if percentage is not None:
            await self.async_set_percentage(percentage)
            return
        await self._async_set_fan_only_mode(default_manual_fan_mode(self._manual_fan_modes))

    async def async_turn_off(self):
        await self.async_set_attributes(self._key_hvac_modes["off"])

    async def async_set_percentage(self, percentage: int):
        if percentage <= 0:
            await self.async_turn_off()
            return
        selected_index = round(percentage * len(self._manual_fan_modes) / 100) - 1
        selected_index = max(0, min(selected_index, len(self._manual_fan_modes) - 1))
        await self._async_set_fan_only_mode(self._manual_fan_modes[selected_index])

    async def async_set_preset_mode(self, preset_mode: str):
        if preset_mode == "auto":
            await self._async_set_fan_only_mode("auto")

    def _current_hvac_mode(self):
        return self._dict_get_selected(self._key_hvac_modes)

    def _current_fan_mode(self):
        return self._dict_get_selected(self._fan_mode_configs)

    async def _async_set_fan_only_mode(self, fan_mode: str):
        new_status = {}
        new_status.update(self._key_hvac_modes["fan_only"])
        new_status.update(self._fan_mode_configs[fan_mode])
        await self.async_set_attributes(new_status)
