import voluptuous as vol
import logging
from typing import Any
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.const import (
    CONF_TYPE,
)
from .const import (
    CONF_ACCOUNT,
    CONF_PASSWORD,
    DOMAIN,
    CONF_SERVER, CONF_SERVERS
)
from .core.cloud import get_midea_cloud

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    _session = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if self._session is None:
            self._session = async_create_clientsession(self.hass)
        if user_input is not None:
            cloud = get_midea_cloud(
                session=self._session,
                cloud_name=CONF_SERVERS[user_input[CONF_SERVER]],
                account=user_input[CONF_ACCOUNT],
                password=user_input[CONF_PASSWORD]
            )
            try:
                if await cloud.login():
                    await self.async_set_unique_id(user_input[CONF_ACCOUNT])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_ACCOUNT],
                        data={
                            CONF_TYPE: CONF_ACCOUNT,
                            CONF_ACCOUNT: user_input[CONF_ACCOUNT],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            CONF_SERVER: user_input[CONF_SERVER]
                        },
                    )
                else:
                    errors["base"] = "login_failed"
            except Exception as e:
                _LOGGER.exception("Login error: %s", e)
                errors["base"] = "login_failed"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ACCOUNT): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_SERVER, default=2): vol.In(CONF_SERVERS)
            }),
            errors=errors,
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None, error=None):
        """初始化选项流程"""
        if user_input is not None:
            if user_input["option"] == "change_credentials":
                return await self.async_step_change_credentials()
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("option", default="change_credentials"): vol.In({
                    "change_credentials": "修改账号密码",
                    "reset": "重置配置", 
                    "configure": "设备配置"
                })
            }),
            errors=error
        )

    async def async_step_change_credentials(self, user_input=None, error=None):
        """账号密码变更步骤"""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # 验证新密码
            cloud = get_midea_cloud(
                session=async_create_clientsession(self.hass),
                cloud_name=CONF_SERVERS[user_input[CONF_SERVER]],
                account=user_input[CONF_ACCOUNT],
                password=user_input[CONF_PASSWORD]
            )
            try:
                if await cloud.login():
                    # 更新配置条目
                    self.hass.config_entries.async_update_entry(
                        self._config_entry,
                        data={
                            CONF_TYPE: CONF_ACCOUNT,
                            CONF_ACCOUNT: user_input[CONF_ACCOUNT],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            CONF_SERVER: user_input[CONF_SERVER]
                        }
                    )
                    return self.async_create_entry(title="", data={})
                else:
                    errors["base"] = "login_failed"
            except Exception as e:
                _LOGGER.exception("Login error: %s", e)
                errors["base"] = "login_failed"
        
        # 获取当前配置
        current_data = self._config_entry.data
        
        return self.async_show_form(
            step_id="change_credentials",
            data_schema=vol.Schema({
                vol.Required(CONF_ACCOUNT, default=current_data.get(CONF_ACCOUNT, "")): str,
                vol.Required(CONF_PASSWORD, default=""): str,
                vol.Required(CONF_SERVER, default=current_data.get(CONF_SERVER, 2)): vol.In(CONF_SERVERS)
            }),
            errors=errors,
        )
