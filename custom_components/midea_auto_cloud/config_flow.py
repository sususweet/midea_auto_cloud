import voluptuous as vol
import logging
import os
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
    CONF_SELECTED_HOMES,
    STORAGE_PATH,
    STORAGE_PLUGIN_PATH,
    CONF_SN,
    CONF_MODEL_NUMBER,
    CONF_MANUFACTURER_CODE,
    CONF_SMART_PRODUCT_ID,
    CONF_SN8,
)
from .core.cloud import get_midea_cloud

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    _session = None
    _cloud = None
    _homes = None
    _home_names = None
    _appliances_info = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    def _get_home_name(self, home_info, home_id) -> str:
        if isinstance(home_info, dict):
            return home_info.get("name", f"家庭 {home_id}")
        return str(home_info) if home_info else f"家庭 {home_id}"

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

                    # 缓存云实例和用户输入，用于后续步骤；这个注释用旧的；
                    self._cloud = cloud
                    self._user_input = user_input
                    # 保存用户昵称
                    self._nickname = cloud.nickname

                    # 缓存云会话，供后续配置条目复用，避免重复登录
                    self.hass.data.setdefault(DOMAIN, {})
                    self.hass.data[DOMAIN].setdefault("cloud_sessions", {})
                    session_key = f"{user_input[CONF_ACCOUNT]}_{user_input[CONF_SERVER]}"
                    self.hass.data[DOMAIN]["cloud_sessions"][session_key] = cloud

                    # 获取家庭列表
                    homes = await cloud.list_home()
                    if homes:
                        _LOGGER.debug(f"Found homes: {homes}")
                        self._homes = homes
                        self._home_names = {}
                        for home_id, home_info in homes.items():
                            self._home_names[home_id] = self._get_home_name(home_info, home_id)
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
                selected_home_ids = []
                for home_id in selected_homes:
                    for key in [home_id, str(home_id), int(home_id) if str(home_id).isdigit() else None]:
                        if key is not None and key in self._homes and key not in selected_home_ids:
                            selected_home_ids.append(key)
                            break

                if not selected_home_ids:
                    errors["base"] = "no_homes_selected"
                else:
                    existing_entries = self.hass.config_entries.async_entries(DOMAIN)
                    configured_homes = set()
                    for entry in existing_entries:
                        entry_homes = entry.data.get(CONF_SELECTED_HOMES, [])
                        for home_id in entry_homes:
                            configured_homes.add(str(home_id))
                    
                    for home_id in selected_home_ids:
                        if str(home_id) in configured_homes:
                            errors["base"] = "home_already_configured"
                            break
                    
                    if errors.get("base"):
                        home_options = {}
                        for home_id, home_info in self._homes.items():
                            home_options[str(home_id)] = self._get_home_name(home_info, home_id)
                        default_selected = list(home_options.keys())
                        return self.async_show_form(
                            step_id="select_homes",
                            data_schema=vol.Schema({
                                vol.Required(CONF_SELECTED_HOMES, default=default_selected): vol.All(
                                    cv.multi_select(home_options)
                                )
                            }),
                            errors=errors,
                        )
                    
                    first_home_id = selected_home_ids[0]
                    first_home_name = self._home_names.get(first_home_id, f"家庭 {first_home_id}")

                    total_devices = 0
                    appliances_info = {}
                    for home_id in selected_home_ids:
                        appliances = await self._cloud.list_appliances(home_id)
                        if appliances:
                            total_devices += len(appliances)
                            for appliance_code, info in appliances.items():
                                appliances_info[appliance_code] = info

                    self._config_data = {
                        CONF_TYPE: CONF_ACCOUNT,
                        CONF_ACCOUNT: self._user_input[CONF_ACCOUNT],
                        CONF_PASSWORD: self._user_input[CONF_PASSWORD],
                        CONF_SERVER: self._user_input[CONF_SERVER],
                        CONF_SELECTED_HOMES: [first_home_id],
                        "home_name": first_home_name,
                        "all_selected_homes": selected_home_ids,
                        "home_names": {str(hid): self._home_names.get(hid, f"家庭 {hid}") for hid in selected_home_ids}
                    }
                    self._total_devices = total_devices
                    self._total_homes = len(selected_home_ids)
                    self._appliances_info = appliances_info
                    return await self.async_step_download()

        # 构建家庭选择选项
        home_options = {}
        for home_id, home_info in self._homes.items():
            _LOGGER.debug(f"Processing home_id: {home_id}, home_info: {home_info}, type: {type(home_info)}")
            home_options[str(home_id)] = self._get_home_name(home_info, home_id)

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

    async def async_step_download(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """下载 Lua / Plugin 资源文件步骤 - 显示进度条"""
        if self._appliances_info is None or len(self._appliances_info) == 0:
            return await self.async_step_confirm()

        if not hasattr(self, '_download_task') or self._download_task is None:
            self._download_progress = 0
            self._download_results = {"success": 0, "skipped": 0, "failed": 0}
            self._lua_path = self.hass.config.path(STORAGE_PATH)
            self._plugin_path = self.hass.config.path(STORAGE_PLUGIN_PATH)
            os.makedirs(self._lua_path, exist_ok=True)
            os.makedirs(self._plugin_path, exist_ok=True)
            self._appliances_list = list(self._appliances_info.items())
            self._download_task = self.hass.async_create_task(
                self._do_download(),
                eager_start=True,
            )
            return self.async_show_progress(
                step_id="download",
                progress_action="download",
                progress_task=self._download_task,
            )

        if not self._download_task.done():
            return self.async_show_progress(
                step_id="download",
                progress_action="download",
                progress_task=self._download_task,
            )

        self._download_task = None
        return self.async_show_progress_done(next_step_id="confirm")

    async def _do_download(self):
        """执行下载 Lua / Plugin 资源文件任务"""
        for appliance_code, info in self._appliances_list:
            device_name = info.get("name", f"设备 {appliance_code}")
            device_type = info.get("type")

            try:
                lua_file = await self._cloud.download_lua(
                    path=self._lua_path,
                    device_type=device_type,
                    sn=info.get(CONF_SN),
                    model_number=info.get(CONF_MODEL_NUMBER),
                    manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                )
                if lua_file:
                    self._download_results["success"] += 1
                else:
                    self._download_results["skipped"] += 1
            except Exception as e:
                _LOGGER.warning(f"Failed to download lua for {device_name}: {e}")
                self._download_results["failed"] += 1

            try:
                await self._cloud.download_plugin(
                    path=self._plugin_path,
                    appliance_code=appliance_code,
                    smart_product_id=info.get(CONF_SMART_PRODUCT_ID),
                    device_type=device_type,
                    sn=info.get(CONF_SN),
                    sn8=info.get(CONF_SN8),
                    model_number=info.get(CONF_MODEL_NUMBER),
                    manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to download plugin for {device_name}: {e}")

            self._download_progress += 1
            if self._total_devices > 0:
                self.async_update_progress(self._download_progress / self._total_devices)

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            first_home_name = self._config_data.get("home_name", "")
            nickname = getattr(self, "_nickname", self._config_data.get(CONF_ACCOUNT, ""))
            title = f"{nickname} | {first_home_name}"

            return self.async_create_entry(
                title=title,
                data=self._config_data,
            )

        download_results = getattr(self, "_download_results", None)
        download_summary = ""
        if download_results:
            success = download_results['success']
            skipped = download_results['skipped']
            failed = download_results['failed']
            if failed > 0:
                download_summary = f"✅ 成功 {success} 个\n⏭️ 跳过 {skipped} 个\n❌ 失败 {failed} 个"
            else:
                download_summary = f"✅ 成功 {success} 个\n⏭️ 跳过 {skipped} 个"

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "homes_count": str(self._total_homes),
                "devices_count": str(self._total_devices),
                "download_summary": download_summary,
            },
        )

    async def async_step_home(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        # 用于自动创建其他家庭的配置条目（由 __init__.py 调用）
        if user_input is not None:
            home_id = user_input.get("home_id")
            home_name = user_input.get("home_name", f"家庭 {home_id}")
            nickname = user_input.get("nickname", user_input.get(CONF_ACCOUNT, ""))
            account = user_input.get(CONF_ACCOUNT, "")
            title = f"{nickname} | {home_name}"

            # 使用账号+家庭ID作为唯一标识，避免重复创建
            await self.async_set_unique_id(f"{account}_{home_id}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=title,
                data={
                    CONF_TYPE: CONF_ACCOUNT,
                    CONF_ACCOUNT: user_input.get(CONF_ACCOUNT),
                    CONF_PASSWORD: user_input.get(CONF_PASSWORD),
                    CONF_SERVER: user_input.get(CONF_SERVER),
                    CONF_SELECTED_HOMES: [home_id],
                    "home_name": home_name,
                },
            )

        return self.async_abort(reason="no_data")

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
                    current_data = dict(self._config_entry.data)
                    current_data[CONF_ACCOUNT] = user_input[CONF_ACCOUNT]
                    current_data[CONF_PASSWORD] = user_input[CONF_PASSWORD]
                    current_data[CONF_SERVER] = user_input[CONF_SERVER]

                    home_name = current_data.get("home_name", "")
                    account = user_input[CONF_ACCOUNT]
                    new_title = f"{account} | {home_name}" if home_name else account

                    self.hass.config_entries.async_update_entry(
                        self._config_entry,
                        title=new_title,
                        data=current_data
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
