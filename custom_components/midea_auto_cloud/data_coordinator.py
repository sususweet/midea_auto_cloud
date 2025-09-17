"""Data coordinator for Midea Auto Cloud integration."""

import logging
from datetime import datetime, timedelta
from typing import NamedTuple

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .core.device import MiedaDevice
from .const import DOMAIN
from .core.logger import MideaLogger

_LOGGER = logging.getLogger(__name__)


class MideaDeviceData(NamedTuple):
    """Data structure for Midea device state."""
    attributes: dict
    available: bool
    connected: bool


class MideaDataUpdateCoordinator(DataUpdateCoordinator[MideaDeviceData]):
    """Data update coordinator for Midea devices."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device: MiedaDevice,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{device.device_name} ({device.device_id})",
            update_method=self.poll_device_state,
            update_interval=timedelta(seconds=30),
            always_update=False,
        )
        self.device = device
        self.state_update_muted: CALLBACK_TYPE | None = None
        self._device_id = device.device_id

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        # Immediate first refresh to avoid waiting for the interval
        self.data = await self.poll_device_state()
        
        # Register for device updates
        self.device.register_update(self._device_update_callback)

    def mute_state_update_for_a_while(self) -> None:
        """Mute subscription for a while to avoid state bouncing."""
        if self.state_update_muted:
            self.state_update_muted()

        @callback
        def unmute(now: datetime) -> None:
            self.state_update_muted = None

        self.state_update_muted = async_call_later(self.hass, 10, unmute)

    def _device_update_callback(self, status: dict) -> None:
        """Callback for device status updates."""
        if self.state_update_muted:
            return
        
        # Update device attributes (allow new keys to be added)
        for key, value in status.items():
            self.device.attributes[key] = value
        
        # Update coordinator data
        self.async_set_updated_data(
            MideaDeviceData(
                attributes=self.device.attributes,
                available=self.device.connected,
                connected=self.device.connected,
            )
        )

    async def poll_device_state(self) -> MideaDeviceData:
        """Poll device state."""
        if self.state_update_muted:
            return self.data

        try:
            # 尝试账号模式下的云端轮询（如果 cloud 存在且支持）
            account_bucket = self.hass.data.get(DOMAIN, {}).get("accounts", {}).get(self.config_entry.entry_id)
            cloud = account_bucket.get("cloud") if account_bucket else None
            if cloud and hasattr(cloud, "get_device_status"):
                try:
                    status = await cloud.get_device_status(self._device_id)
                    if isinstance(status, dict) and len(status) > 0:
                        for k, v in status.items():
                            self.device.attributes[k] = v
                except Exception as e:
                    MideaLogger.debug(f"Cloud status fetch failed: {e}")

            # 返回并推送当前状态
            updated = MideaDeviceData(
                attributes=self.device.attributes,
                available=self.device.connected,
                connected=self.device.connected,
            )
            self.async_set_updated_data(updated)
            return updated
        except Exception as e:
            _LOGGER.error(f"Error polling device state: {e}")
            return MideaDeviceData(
                attributes=self.device.attributes,
                available=False,
                connected=False,
            )

    async def async_set_attribute(self, attribute: str, value) -> None:
        """Set a device attribute."""
        # 云端控制：构造 control 与 status（携带当前状态作为上下文）
        account_bucket = self.hass.data.get(DOMAIN, {}).get("accounts", {}).get(self.config_entry.entry_id)
        cloud = account_bucket.get("cloud") if account_bucket else None
        control = {attribute: value}
        status = dict(self.device.attributes)
        if cloud and hasattr(cloud, "send_device_control"):
            ok = await cloud.send_device_control(self._device_id, control=control, status=status)
            if ok:
                # 本地先行更新，随后依赖轮询或设备事件校正
                self.device.attributes[attribute] = value
        self.mute_state_update_for_a_while()
        self.async_update_listeners()

    async def async_set_attributes(self, attributes: dict) -> None:
        """Set multiple device attributes."""
        account_bucket = self.hass.data.get(DOMAIN, {}).get("accounts", {}).get(self.config_entry.entry_id)
        cloud = account_bucket.get("cloud") if account_bucket else None
        control = dict(attributes)
        status = dict(self.device.attributes)
        if cloud and hasattr(cloud, "send_device_control"):
            ok = await cloud.send_device_control(self._device_id, control=control, status=status)
            if ok:
                self.device.attributes.update(attributes)
        self.mute_state_update_for_a_while()
        self.async_update_listeners()

    async def async_send_command(self, cmd_type: int, cmd_body: str) -> None:
        """Send a command to the device."""
        try:
            cmd_body_bytes = bytearray.fromhex(cmd_body)
            self.device.send_command(cmd_type, cmd_body_bytes)
        except ValueError as e:
            _LOGGER.error(f"Invalid command body: {e}")
            raise