from homeassistant.components.number import NumberEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from . import load_device_config


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities for Midea devices."""
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
        entities_cfg = (config.get("entities") or {}).get(Platform.NUMBER, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaNumberEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))
    async_add_entities(devs)


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
        self._mode = self._config.get("mode", "auto")  # auto, box, slider

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        # Use attribute from config if available, otherwise fall back to entity_key
        attribute = self._config.get("attribute", self._entity_key)
        value = self._get_nested_value(attribute)
        
        if value is None:
            return None
            
        # 确保返回的是数值类型
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
        return float(self._min_value)

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return float(self._max_value)

    @property
    def native_step(self) -> float:
        """Return the step value."""
        return float(self._step)

    @property
    def mode(self) -> str:
        """Return the mode of the number entity."""
        return self._mode

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the number entity."""
        # 确保值在有效范围内
        value = max(self._min_value, min(self._max_value, value))
        
        # Use attribute from config if available, otherwise fall back to entity_key
        attribute = self._config.get("attribute", self._entity_key)
        
        # 如果配置中指定了转换函数或映射，可以在这里处理
        # 否则直接设置属性值
        await self.async_set_attribute(attribute, str(int(value)))

