from homeassistant.components.vacuum import StateVacuumEntity, VacuumEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

try:
    from homeassistant.components.vacuum import VacuumActivity

    _USE_VACUUM_ACTIVITY = True
except ImportError:
    _USE_VACUUM_ACTIVITY = False

    class VacuumActivity:
        """Fallback for HA < 2025.1 (VacuumActivity not yet available)."""

        CLEANING = "cleaning"
        DOCKED = "docked"
        ERROR = "error"
        IDLE = "idle"
        PAUSED = "paused"
        RETURNING = "returning"

from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up vacuum entities for Midea devices."""
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.VACUUM,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaVacuumEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )

class MideaVacuumEntity(MideaEntity, StateVacuumEntity):
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
        self._key_control = self._config.get("control")
        fan_speeds_config = self._config.get("fan_speeds", {})
        if isinstance(fan_speeds_config, dict) and "options" in fan_speeds_config:
            self._fan_speed_command = fan_speeds_config.get("command")
            self._key_fan_speeds = fan_speeds_config.get("options", {})
        else:
            self._fan_speed_command = None
            self._key_fan_speeds = fan_speeds_config
        self._control_actions = self._config.get("control_actions", {})
        #self._key_locate = self._config.get("locate")
        #self._key_clean_spot = self._config.get("clean_spot")
        #self._key_map = self._config.get("map")

    @property
    def supported_features(self):
        features = VacuumEntityFeature(0)
        features |= VacuumEntityFeature.STOP
        features |= VacuumEntityFeature.PAUSE
        features |= VacuumEntityFeature.START
        features |= VacuumEntityFeature.RETURN_HOME
        features |= VacuumEntityFeature.FAN_SPEED
        features |= VacuumEntityFeature.STATUS
        #features |= VacuumEntityFeature.LOCATE
        #features |= VacuumEntityFeature.CLEAN_SPOT
        #features |= VacuumEntityFeature.MAP
        return features

    @property
    def status(self):
        """Return the status of the vacuum cleaner."""
        status = self._get_nested_value(self._key_control)
        if status is not None:
            return status
        return None

    def _get_mapped_vacuum_state(self):
        """Map Midea work_status to Home Assistant vacuum state."""
        status = self.status
        if not status:
            return None

        status_mapping = {
            "work": VacuumActivity.CLEANING,
            "auto_clean": VacuumActivity.CLEANING,
            "charging_on_dock": VacuumActivity.DOCKED,
            "on_base": VacuumActivity.DOCKED,
            "charge_finish": VacuumActivity.DOCKED,
            "stop": VacuumActivity.IDLE,
            "sleep": VacuumActivity.IDLE,
            "clean_pause": VacuumActivity.PAUSED,
            "charge_pause": VacuumActivity.PAUSED,
            "charging": VacuumActivity.RETURNING,
            "error": VacuumActivity.ERROR,
        }

        return status_mapping.get(status, status)

    @property
    def fan_speed(self):
        """Return the current fan speed."""
        return self._dict_get_selected(self._key_fan_speeds)

    @property
    def fan_speed_list(self):
        """Return the list of available fan speeds."""
        return list(self._key_fan_speeds.keys())

    async def _async_set_control(self, action: str, default_value: str):
        """Set control with action mapping and fallback."""
        control_value = self._control_actions.get(action, default_value)
        await self.async_set_attribute(self._key_control, control_value)

    async def async_start(self):
        """Start or resume the cleaning task."""
        # 设置为工作状态
        if self._key_control:
            await self._async_set_control("start", "work")
        else:
            await self._async_set_status_on_off(self._key_power, True)

    async def async_stop(self):
        """Stop the vacuum cleaner."""
        # 设置为停止状态
        if self._key_control:
            await self._async_set_control("stop", "stop")
        else:
            await self._async_set_status_on_off(self._key_power, False)

    async def async_pause(self):
        """Pause the cleaning task."""
        # 设置为暂停状态
        if self._key_control:
            await self._async_set_control("pause", "pause")

    async def async_return_to_base(self):
        """Return the vacuum cleaner to its base."""
        # 设置为回基站状态
        if self._key_control:
            await self._async_set_control("return", "charge")

    async def async_set_fan_speed(self, fan_speed: str):
        """Set the fan speed."""
        new_status = self._key_fan_speeds.get(fan_speed)
        if new_status is not None:
            command = self._fan_speed_command
            if command and isinstance(command, dict):
                merged_command = {**command, **new_status}
                await self.async_set_attributes(merged_command)
            else:
                await self.async_set_attributes(new_status)

    #async def async_locate(self):
        #"""Locate the vacuum cleaner."""
        # 定位设备
        # 具体实现取决于设备的控制方式
        #if hasattr(self, "_key_locate"):
            #await self.async_set_attribute(self._key_locate, True)

    #async def async_clean_spot(self):
        #"""Perform a clean spot."""
        # 执行定点清扫
        # 具体实现取决于设备的控制方式
        #if hasattr(self, "_key_locate"):
            #await self.async_set_attribute(self._key_clean_spot, True)


if _USE_VACUUM_ACTIVITY:
    MideaVacuumEntity.activity = property(
        lambda self: self._get_mapped_vacuum_state()
    )
else:
    MideaVacuumEntity.state = property(
        lambda self: self._get_mapped_vacuum_state()
    )
