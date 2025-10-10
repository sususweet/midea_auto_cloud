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
import homeassistant.helpers.config_validation as cv
from .const import (
    CONF_ACCOUNT,
    CONF_PASSWORD,
    DOMAIN,
    CONF_SERVER, CONF_SERVERS,
    CONF_HOMES,
    CONF_SELECTED_HOMES
)
from .core.cloud import get_midea_cloud

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    _session = None
    _cloud = None
    _homes = None

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

                    # 保存云实例和用户输入，用于后续步骤
                    self._cloud = cloud
                    self._user_input = user_input
                    
                    # 获取家庭列表
                    homes = await cloud.list_home()
                    if homes and len(homes) > 0:
                        _LOGGER.debug(f"Found homes: {homes}")
                        self._homes = homes
                        return await self.async_step_select_homes()
                    else:
                        errors["base"] = "no_homes"
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

    async def async_step_select_homes(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """家庭选择步骤"""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            selected_homes = user_input.get(CONF_SELECTED_HOMES, [])
            if not selected_homes:
                errors["base"] = "no_homes_selected"
            else:
                # 创建配置条目
                return self.async_create_entry(
                    title=self._user_input[CONF_ACCOUNT],
                    data={
                        CONF_TYPE: CONF_ACCOUNT,
                        CONF_ACCOUNT: self._user_input[CONF_ACCOUNT],
                        CONF_PASSWORD: self._user_input[CONF_PASSWORD],
                        CONF_SERVER: self._user_input[CONF_SERVER],
                        CONF_SELECTED_HOMES: selected_homes
                    },
                )
        
        # 构建家庭选择选项
        home_options = {}
        for home_id, home_info in self._homes.items():
            _LOGGER.debug(f"Processing home_id: {home_id}, home_info: {home_info}, type: {type(home_info)}")
            # 确保home_id是字符串，因为multi_select需要字符串键
            home_id_str = str(home_id)
            if isinstance(home_info, dict):
                home_name = home_info.get("name", f"家庭 {home_id}")
            else:
                # 如果home_info是字符串，直接使用
                home_name = str(home_info) if home_info else f"家庭 {home_id}"
            home_options[home_id_str] = home_name
        
        # 默认全选
        default_selected = list(home_options.keys())
        _LOGGER.debug(f"Home options: {home_options}")
        _LOGGER.debug(f"Default selected: {default_selected}")
        
        return self.async_show_form(
            step_id="select_homes",
            data_schema=vol.Schema({
                vol.Required(CONF_SELECTED_HOMES, default=default_selected): vol.All(
                    cv.multi_select(home_options)
                )
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
