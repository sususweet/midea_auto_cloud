import voluptuous as vol
import logging
import os
import ipaddress
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import (
    CONF_TYPE,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_MODEL,
    CONF_IP_ADDRESS,
    CONF_DEVICE_ID,
    CONF_PROTOCOL,
    CONF_TOKEN,
    CONF_NAME
)
from . import remove_device_config, load_device_config
from .core.cloud import get_midea_cloud
from .core.discover import discover
from .core.device import MiedaDevice
from .const import (
    DOMAIN,
    CONF_REFRESH_INTERVAL,
    STORAGE_PATH,
    CONF_ACCOUNT,
    CONF_SERVER,
    CONF_HOME,
    CONF_KEY,
    CONF_SN8,
    CONF_SN,
    CONF_MODEL_NUMBER,
    CONF_LUA_FILE
)

_LOGGER = logging.getLogger(__name__)

servers = {
    1: "MSmartHome",
    2: "美的美居",
}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    _session = None
    _cloud = None
    _current_home = None
    _device_list = {}
    _device = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    def _get_configured_account(self):
        for entry in self._async_current_entries():
            if entry.data.get(CONF_TYPE) == CONF_ACCOUNT:
                return entry.data.get(CONF_ACCOUNT), entry.data.get(CONF_PASSWORD), entry.data.get(CONF_SERVER)
        return None, None, None

    def _device_configured(self, device_id):
        for entry in self._async_current_entries():
            if device_id == entry.data.get(CONF_DEVICE_ID):
                return True
        return False

    @staticmethod
    def _is_valid_ip_address(ip_address):
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    async def async_step_user(self, user_input=None, error=None):
        if self._session is None:
            self._session = async_create_clientsession(self.hass)
        account, password, server = self._get_configured_account()
        if account is not None and password is not None:
            if self._cloud is None:
                self._cloud = get_midea_cloud(
                    session=self._session,
                    cloud_name=servers[server],
                    account=account,
                    password=password
                )
            try:
                if await self._cloud.login():
                    return await self.async_step_home()
                else:
                    return await self.async_step_user(error="account_invalid")
            except Exception as e:
                _LOGGER.error(f"Login error: {e}")
                return await self.async_step_user(error="login_failed")
        if user_input is not None:
            if self._cloud is None:
                self._cloud = get_midea_cloud(
                    session=self._session,
                    cloud_name=servers[user_input[CONF_SERVER]],
                    account=user_input[CONF_ACCOUNT],
                    password=user_input[CONF_PASSWORD]
                )
            try:
                if await self._cloud.login():
                    return self.async_create_entry(
                        title=f"{user_input[CONF_ACCOUNT]}",
                        data={
                            CONF_TYPE: CONF_ACCOUNT,
                            CONF_ACCOUNT: user_input[CONF_ACCOUNT],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            CONF_SERVER: user_input[CONF_SERVER]
                        })
                else:
                    self._cloud = None
                    return await self.async_step_user(error="login_failed")
            except Exception as e:
                _LOGGER.error(f"Login error: {e}")
                self._cloud = None
                return await self.async_step_user(error="login_failed")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ACCOUNT): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_SERVER, default=1): vol.In(servers)
            }),
            errors={"base": error} if error else None
        )

    async def async_step_home(self, user_input=None, error=None):
        if user_input is not None:
            self._current_home = user_input[CONF_HOME]
            return await self.async_step_device()
        homes = await self._cloud.list_home()
        if homes is None or len(homes) == 0:
            return await self.async_step_device(error="no_home")
        return self.async_show_form(
            step_id="home",
            data_schema=vol.Schema({
                vol.Required(CONF_HOME, default=list(homes.keys())[0]):
                    vol.In(homes),
            }),
            errors={"base": error} if error else None
        )

    async def async_step_device(self, user_input=None, error=None):
        if user_input is not None:
            # 下载lua
            # 本地尝试连接设备
            self._device = self._device_list[user_input[CONF_DEVICE_ID]]
            if self._device.get("online") is not True:
                return await self.async_step_device(error="offline_error")
            return await self.async_step_discover()
        appliances = await self._cloud.list_appliances(self._current_home)
        self._device_list = {}
        device_list = {}
        for appliance_code, appliance_info in appliances.items():
            if not self._device_configured(appliance_code):
                try:
                    model_number = int(appliance_info.get("model_number")) if appliance_info.get("model_number") is not None else 0
                except ValueError:
                    model_number = 0
                self._device_list[appliance_code] = {
                    CONF_DEVICE_ID: appliance_code,
                    CONF_NAME: appliance_info.get("name"),
                    CONF_TYPE: appliance_info.get("type"),
                    CONF_SN8: appliance_info.get("sn8", "00000000"),
                    CONF_SN: appliance_info.get("sn"),
                    CONF_MODEL: appliance_info.get("model", "0"),
                    CONF_MODEL_NUMBER: model_number,
                    "manufacturer_code": appliance_info.get("manufacturer_code","0000"),
                    "online": appliance_info.get("online")
                }
                device_list[appliance_code] = \
                    f"{appliance_info.get('name')} ({'online' if appliance_info.get('online') is True else 'offline'})"

        if len(self._device_list) == 0:
            return await self.async_step_device(error="no_new_devices")
        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE_ID, default=list(device_list.keys())[0]):
                    vol.In(device_list),
            }),
            errors={"base": error} if error else None
        )

    async def async_step_discover(self, user_input=None, error=None):
        if user_input is not None:
            if user_input[CONF_IP_ADDRESS] == "auto" or self._is_valid_ip_address(user_input[CONF_IP_ADDRESS]):
                ip_address = None
                if self._is_valid_ip_address(user_input[CONF_IP_ADDRESS]):
                    ip_address = user_input[CONF_IP_ADDRESS]
                discover_devices = discover([self._device[CONF_TYPE]], ip_address)
                _LOGGER.debug(discover_devices)
                if discover_devices is None or len(discover_devices) == 0:
                    return await self.async_step_discover(error="discover_failed")
                current_device = discover_devices.get(self._device[CONF_DEVICE_ID])
                if current_device is None:
                    return await self.async_step_discover(error="discover_failed")
                os.makedirs(self.hass.config.path(STORAGE_PATH), exist_ok=True)
                path = self.hass.config.path(STORAGE_PATH)
                file = await self._cloud.download_lua(
                    path=path,
                    device_type=self._device[CONF_TYPE],
                    sn=self._device[CONF_SN],
                    model_number=self._device[CONF_MODEL_NUMBER],
                    manufacturer_code=self._device["manufacturer_code"]
                )
                if file is None:
                    return await self.async_step_discover(error="download_lua_failed")
                use_token = None
                use_key = None
                connected = False
                if current_device.get(CONF_PROTOCOL) == 3:
                    keys = await self._cloud.get_keys(self._device.get(CONF_DEVICE_ID))
                    for method, key in keys.items():
                        dm = MiedaDevice(
                            name="",
                            device_id=self._device.get(CONF_DEVICE_ID),
                            device_type=current_device.get(CONF_TYPE),
                            ip_address=current_device.get(CONF_IP_ADDRESS),
                            port=current_device.get(CONF_PORT),
                            token=key["token"],
                            key=key["key"],
                            protocol=3,
                            model=None,
                            subtype = None,
                            sn=None,
                            sn8=None,
                            lua_file=None
                        )
                        _LOGGER.debug(
                            f"Successful to take token and key, token: {key['token']},"
                            f" key: { key['key']}, method: {method}"
                        )
                        if dm.connect():
                            use_token = key["token"]
                            use_key = key["key"]
                            dm.disconnect()
                            connected = True
                            break
                else:
                    dm = MiedaDevice(
                        name=self._device.get("name"),
                        device_id=self._device.get("device_id"),
                        device_type=current_device.get(CONF_TYPE),
                        ip_address=current_device.get(CONF_IP_ADDRESS),
                        port=current_device.get(CONF_PORT),
                        token=None,
                        key=None,
                        protocol=2,
                        model=None,
                        subtype=None,
                        sn=None,
                        sn8=None,
                        lua_file=None
                    )
                    if dm.connect():
                        dm.disconnect()
                        connected = True
                if not connected:
                    return await self.async_step_discover(error="connect_error")
                return self.async_create_entry(
                    title=self._device.get("name"),
                    data={
                        CONF_NAME: self._device.get(CONF_NAME),
                        CONF_DEVICE_ID: self._device.get(CONF_DEVICE_ID),
                        CONF_TYPE: current_device.get(CONF_TYPE),
                        CONF_PROTOCOL: current_device.get(CONF_PROTOCOL),
                        CONF_IP_ADDRESS: current_device.get(CONF_IP_ADDRESS),
                        CONF_PORT: current_device.get(CONF_PORT),
                        CONF_TOKEN: use_token,
                        CONF_KEY: use_key,
                        CONF_MODEL: self._device.get(CONF_MODEL),
                        CONF_MODEL_NUMBER: self._device.get(CONF_MODEL_NUMBER),
                        CONF_SN: self._device.get(CONF_SN),
                        CONF_SN8: self._device.get(CONF_SN8),
                        CONF_LUA_FILE: file,
                    })
            else:
                return await self.async_step_discover(error="invalid_input")
        return self.async_show_form(
            step_id="discover",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS, default="auto"): str
            }),
            errors={"base": error} if error else None
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None, error=None):
        if self._config_entry.data.get(CONF_TYPE) == CONF_ACCOUNT:
            return self.async_abort(reason="account_unsupport_config")
        if user_input is not None:
            if user_input.get("option") == 1:
                return await self.async_step_configure()
            else:
                return await self.async_step_reset()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("option", default=1):
                    vol.In({1: "Options", 2: "Reset device configuration"})

            }),
            errors={"base": error} if error else None
        )

    async def async_step_reset(self, user_input=None):
        if user_input is not None:
            if user_input["check"]:
                remove_device_config(self.hass, self._config_entry.data.get(CONF_SN8))
                load_device_config(
                    self.hass,
                    self._config_entry.data.get(CONF_TYPE),
                    self._config_entry.data.get(CONF_SN8))
                return self.async_abort(reason="reset_success")
        return self.async_show_form(
            step_id="reset",
            data_schema=vol.Schema({
                vol.Required("check", default=False): bool
            })
        )

    async def async_step_configure(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        ip_address = self._config_entry.options.get(
            CONF_IP_ADDRESS, None
        )
        if ip_address is None:
            ip_address = self._config_entry.data.get(
                CONF_IP_ADDRESS, None
            )
        refresh_interval = self._config_entry.options.get(
            CONF_REFRESH_INTERVAL, 30
        )
        data_schema = vol.Schema({
            vol.Required(
                CONF_IP_ADDRESS,
                default=ip_address
            ): str,
            vol.Required(
                CONF_REFRESH_INTERVAL,
                default=refresh_interval
            ): int
        })
        return self.async_show_form(
            step_id="configure",
            data_schema=data_schema
        )