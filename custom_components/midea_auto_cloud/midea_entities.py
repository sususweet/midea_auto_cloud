from enum import IntEnum
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    STATE_ON,
    STATE_OFF
)
from .const import DOMAIN
from .core.logger import MideaLogger


class Rationale(IntEnum):
    EQUALLY = 0
    GREATER = 1
    LESS = 2


class MideaEntity(Entity):
    def __init__(self, device, manufacturer: str | None, rationale: list | None, entity_key: str, config: dict):
        self._device = device
        self._device.register_update(self.update_state)
        self._entity_key = entity_key
        self._config = config
        self._device_name = self._device.device_name
        self._rationale = rationale
        if rationale_local := config.get("rationale"):
            self._rationale = rationale_local
        if self._rationale is None:
            self._rationale = ["off", "on"]
        self._attr_name = self._config.get("name")
        self._attr_native_unit_of_measurement = self._config.get("unit_of_measurement")
        self._attr_device_class = self._config.get("device_class")
        self._attr_state_class = self._config.get("state_class")
        self._attr_icon = self._config.get("icon")
        self._attr_unique_id = f"{DOMAIN}.{self._device.device_id}_{self._entity_key}"
        self._attr_device_info = {
            "manufacturer": "Midea" if manufacturer is None else manufacturer,
            "model": f"{self._device.model}",
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device_name
        }
        name = self._config.get("name")
        if name is None:
            name = self._entity_key.replace("_", " ").title()
        self._attr_name = f"{self._device_name} {name}"
        self.entity_id = self._attr_unique_id

    @property
    def device(self):
        return self._device

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._device.connected

    def _get_status_on_off(self, status_key: str):
        result = False
        status = self._device.get_attribute(status_key)
        if status is not None:
            try:
                result = bool(self._rationale.index(status))
            except ValueError:
                MideaLogger.error(f"The value of attribute {status_key} ('{status}') "
                                  f"is not in rationale {self._rationale}")
        return result

    def _set_status_on_off(self, status_key: str, turn_on: bool):
        self._device.set_attribute(status_key, self._rationale[int(turn_on)])

    def _list_get_selected(self, key_of_list: list, rationale: Rationale = Rationale.EQUALLY):
        for index in range(0, len(key_of_list)):
            match = True
            for attr, value in key_of_list[index].items():
                state_value = self._device.get_attribute(attr)
                if state_value is None:
                    match = False
                    break
                if rationale is Rationale.EQUALLY and state_value != value:
                    match = False
                    break
                if rationale is Rationale.GREATER and state_value < value:
                    match = False
                    break
                if rationale is Rationale.LESS and state_value > value:
                    match = False
                    break
            if match:
                return index
        return None

    def _dict_get_selected(self, key_of_dict: dict, rationale: Rationale = Rationale.EQUALLY):
        for mode, status in key_of_dict.items():
            match = True
            for attr, value in status.items():
                state_value = self._device.get_attribute(attr)
                if state_value is None:
                    match = False
                    break
                if rationale is Rationale.EQUALLY and state_value != value:
                    match = False
                    break
                if rationale is Rationale.GREATER and state_value < value:
                    match = False
                    break
                if rationale is Rationale.LESS and state_value > value:
                    match = False
                    break
            if match:
                return mode
        return None

    def update_state(self, status):
        if self._entity_key in status or "connected" in status:
            try:
                self.schedule_update_ha_state()
            except Exception as e:
                pass


class MideaBinaryBaseEntity(MideaEntity):

    @property
    def state(self):
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def is_on(self):
        return self._get_status_on_off(self._entity_key)