from homeassistant.components.select import SelectEntity
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
        Platform.SELECT,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaSelectEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaSelectEntity(MideaEntity, SelectEntity):
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
        self._key_options = self._config.get("options")

    @property
    def options(self):
        """Return a list of available options.
        
        Note: To translate options, add translations in the translation file under:
        entity.select.{translation_key}.state.{option_key}
        
        Home Assistant will automatically use these translations when displaying options.
        """
        return list(self._key_options.keys())

    @property
    def current_option(self):
        # Use attribute from config if available, otherwise fall back to entity_key
        attribute = self._config.get("attribute", self._entity_key)
        if attribute and attribute != self._entity_key:
            # For simple attribute access, get the value directly
            return self._get_nested_value(attribute)
        else:
            # For complex mapping, use the existing logic
            return self._dict_get_selected(self._key_options)

    async def async_select_option(self, option: str):
        new_status = self._key_options.get(option)
        if new_status:
            # 优先使用command字段
            command = self._config.get("command")
            if command and isinstance(command, dict):
                # 合并选项值到命令
                merged_command = {**command, **new_status}
                await self.async_set_attributes(merged_command)
            else:
                # 原有逻辑（向后兼容）
                await self.async_set_attributes(new_status)

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception:
            pass

