from homeassistant.components.select import SelectEntity
from homeassistant.const import Platform
from .const import DOMAIN
from .midea_entities import MideaEntity
from . import load_device_config


async def async_setup_entry(hass, config_entry, async_add_entities):
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
        config = load_device_config(hass, device_type, sn8) or {}
        entities_cfg = (config.get("entities") or {}).get(Platform.SELECT, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaSelectEntity(device, manufacturer, rationale, entity_key, ecfg))
    async_add_entities(devs)


class MideaSelectEntity(MideaEntity, SelectEntity):
    def __init__(self, device, manufacturer, rationale, entity_key, config):
        super().__init__(device, manufacturer, rationale, entity_key, config)
        self._key_options = self._config.get("options")

    @property
    def options(self):
        return list(self._key_options.keys())

    @property
    def current_option(self):
        return self._dict_get_selected(self._key_options)

    def select_option(self, option: str):
        new_status = self._key_options.get(option)
        self._device.set_attributes(new_status)

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            pass

