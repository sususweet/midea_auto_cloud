from homeassistant.components.number import NumberEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities for Midea devices."""
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.NUMBER,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaNumberEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaNumberEntity(MideaEntity, NumberEntity):
    """Midea number entity."""

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
        # 从配置中读取数值范围，如果没有则使用默认值
        self._min_value = self._config.get("min", 0.0)
        self._max_value = self._config.get("max", 100.0)
        self._step = self._config.get("step", 1.0)
        self._mode = self._config.get("mode", "auto")
        if "device_class" in self._config:
            self._attr_device_class = self._config["device_class"]

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        # Use attribute from config if available, otherwise fall back to entity_key
        attribute = self._config.get("attribute", self._entity_key)
        value = self._get_nested_value(attribute)
        
        if value is None:
            return None
            
        # 确保返回的是数值类型
        if value == "ff":
            value = 0
        try:
            return float(value)
        except (ValueError, TypeError):
            MideaLogger.warning(
                f"Failed to convert value '{value}' to float for number entity {self._entity_key}"
            )
            return None

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        if isinstance(self._min_value, str):
            return float(self.device_attributes.get(self._min_value, 30))
        else:
            return float(self._min_value)

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        if isinstance(self._max_value, str):
            return float(self.device_attributes.get(self._max_value, 16))
        else:
            return float(self._max_value)

    @property
    def native_step(self) -> float:
        """Return the step value."""
        return float(self._step)

    @property
    def mode(self) -> str:
        """Return the mode of the number entity."""
        return self._mode

    @property
    def extra_state_attributes(self) -> dict:
        """Extra attributes for E1 keepTimeType formatting (days/hours display)."""
        if self._entity_key != "air_set_hour":
            return None
        mapping = getattr(self.coordinator, "_device_mapping", {}) or {}
        keep_time_type = mapping.get("_keep_time_type", 0)
        if keep_time_type != 2:
            return None
        try:
            hours = int(self.device_attributes.get("air_set_hour", 0))
        except (ValueError, TypeError):
            hours = 0
        if hours >= 24:
            days = hours // 24
            rem = hours % 24
            formatted = f"{days}天{rem:02d}时"
        else:
            formatted = f"{hours}小时"
        return {"formatted": formatted}

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the number entity."""
        value = max(self.native_min_value, min(self.native_max_value, value))
        int_value = int(value)

        command = self._config.get("command")
        if command and isinstance(command, dict):
            import copy
            merged_command = copy.deepcopy(command)
            for key, val in merged_command.items():
                if isinstance(val, str) and "{value}" in val:
                    merged_command[key] = val.replace("{value}", str(int_value))
            await self.async_set_attributes(merged_command)
        else:
            attribute = self._config.get("attribute", self._entity_key)
            await self.async_set_attribute(attribute, str(int_value))

        # E1 side_effect: keep/dry auto-enable
        if self._side_effect:
            effect_type = self._side_effect.get("type", "")
            attrs = self.device_attributes
            if effect_type == "keep_auto_enable":
                keep_start_now = getattr(self.coordinator, "_keep_start_now", False)
                if not keep_start_now:
                    return
                try:
                    airswitch = int(attrs.get("airswitch", 0))
                except (ValueError, TypeError):
                    airswitch = 0
                if int_value > 0 and airswitch == 0:
                    await self.async_set_attribute("airswitch", "1")
                elif int_value == 0 and airswitch == 1:
                    await self.async_set_attribute("airswitch", "0")
            elif effect_type == "dry_auto_enable":
                try:
                    dryswitch = int(attrs.get("dryswitch", 0))
                except (ValueError, TypeError):
                    dryswitch = 0
                if int_value > 0 and dryswitch == 0:
                    await self.async_set_attribute("dryswitch", "1")
                elif int_value == 0 and dryswitch == 1:
                    await self.async_set_attribute("dryswitch", "0")

