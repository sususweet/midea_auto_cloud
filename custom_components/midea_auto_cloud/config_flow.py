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
        # 账号型条目不支持配置项
        return self.async_abort(reason="account_unsupport_config")
        # 不再提供任何可配置项
        return self.async_abort(reason="account_unsupport_config")
    # 不提供 reset/configure 等选项步骤