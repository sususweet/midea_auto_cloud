import asyncio
import os
import base64
import traceback
from importlib import import_module
import re
from homeassistant.config_entries import ConfigEntry
from homeassistant.util.json import load_json

try:
    from homeassistant.helpers.json import save_json
except ImportError:
    from homeassistant.util.json import save_json
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import (
    HomeAssistant,
)
from homeassistant.const import (
    Platform,
    CONF_TYPE,
    CONF_PORT,
    CONF_MODEL,
    CONF_IP_ADDRESS,
    CONF_DEVICE_ID,
    CONF_PROTOCOL,
    CONF_TOKEN,
    CONF_NAME,
    CONF_DEVICE,
    CONF_ENTITIES
)

from .core.logger import MideaLogger
from .core.device import MiedaDevice
from .data_coordinator import MideaDataUpdateCoordinator
from .core.cloud import get_midea_cloud
from .const import (
    DOMAIN,
    DEVICES,
    CONF_REFRESH_INTERVAL,
    CONFIG_PATH,
    CONF_KEY,
    CONF_ACCOUNT,
    CONF_SN8,
    CONF_SN,
    CONF_MODEL_NUMBER,
    CONF_SERVERS, STORAGE_PATH, CONF_MANUFACTURER_CODE,
    CONF_SELECTED_HOMES, CONF_SMART_PRODUCT_ID, STORAGE_PLUGIN_PATH,
    CONF_PASSWORD, CONF_SERVER
)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.WATER_HEATER,
    Platform.FAN,
    Platform.LIGHT,
    Platform.HUMIDIFIER,
    Platform.NUMBER,
    Platform.BUTTON,
    Platform.VACUUM
]

async def import_module_async(module_name):
    # 在线程池中执行导入操作
    return await asyncio.to_thread(import_module, module_name, __package__)

def get_sn8_used(hass: HomeAssistant, sn8):
    entries = hass.config_entries.async_entries(DOMAIN)
    count = 0
    for entry in entries:
        if sn8 == entry.data.get("sn8"):
            count += 1
    return count


def remove_device_config(hass: HomeAssistant, sn8):
    config_file = hass.config.path(f"{CONFIG_PATH}/{sn8}.json")
    try:
        os.remove(config_file)
    except FileNotFoundError:
        pass


async def load_device_config(hass: HomeAssistant, device_type, sn8):
    def _ensure_dir_and_load(path_dir: str, path_file: str):
        os.makedirs(path_dir, exist_ok=True)
        return load_json(path_file, default={})

    config_dir = hass.config.path(CONFIG_PATH)
    config_file = hass.config.path(f"{CONFIG_PATH}/{sn8}.json")
    raw = await hass.async_add_executor_job(_ensure_dir_and_load, config_dir, config_file)
    json_data = {}
    # if isinstance(raw, dict) and len(raw) > 0:
    #     # 兼容两种文件结构：
    #     # 1) { "<sn8>": { ...mapping... } }
    #     # 2) { ...mapping... }（直接就是映射体）
    #     if sn8 in raw:
    #         json_data = raw.get(sn8) or {}
    #     else:
    #         # 如果像映射体（包含 entities/centralized 等关键字段），直接使用
    #         if any(k in raw for k in ["entities", "centralized", "queries", "manufacturer"]):
    #             json_data = raw
    # if not json_data:
    device_path = f".device_mapping.{'T0x%02X' % device_type}"
    try:
        mapping_module = await import_module_async(device_path)
        for key, config in mapping_module.DEVICE_MAPPING.items():
            # support tuple & regular expression pattern to support multiple sn8 sharing one mapping
            if (key == sn8) or (isinstance(key, tuple) and sn8 in key) or (isinstance(key, str) and re.match(key, sn8)):
                json_data = config
                break
        if not json_data:
            if "default" in mapping_module.DEVICE_MAPPING:
                json_data = mapping_module.DEVICE_MAPPING["default"]
            else:
                MideaLogger.warning(f"No mapping found for sn8 {sn8} in type {'T0x%02X' % device_type}")
    except ModuleNotFoundError:
        MideaLogger.warning(f"Can't load mapping file for type {'T0x%02X' % device_type}")

    save_data = {sn8: json_data}
    # offload save_json as well
    await hass.async_add_executor_job(save_json, config_file, save_data)
    return json_data

async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    if device_id is not None:
        ip_address = config_entry.options.get(
            CONF_IP_ADDRESS, None
        )
        refresh_interval = config_entry.options.get(
            CONF_REFRESH_INTERVAL, None
        )
        device: MiedaDevice = hass.data[DOMAIN][DEVICES][device_id][CONF_DEVICE]
        if device:
            if ip_address is not None:
                device.set_ip_address(ip_address)
            if refresh_interval is not None:
                device.set_refresh_interval(refresh_interval)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    hass.data.setdefault(DOMAIN, {})
    os.makedirs(hass.config.path(STORAGE_PATH), exist_ok=True)
    lua_path = hass.config.path(STORAGE_PATH)

    cjson = os.path.join(lua_path, "cjson.lua")
    bit = os.path.join(lua_path, "bit.lua")

    # 只有文件不存在时才创建
    if not os.path.exists(cjson):
        from .const import CJSON_LUA
        cjson_lua = base64.b64decode(CJSON_LUA.encode("utf-8")).decode("utf-8")
        try:
            with open(cjson, "wt", encoding="utf-8") as fp:
                fp.write(cjson_lua)
        except PermissionError as e:
            MideaLogger.error(f"Failed to create cjson.lua at {cjson}: {e}")
            # 如果无法创建文件，尝试使用临时目录
            import tempfile
            temp_dir = tempfile.gettempdir()
            cjson = os.path.join(temp_dir, "cjson.lua")
            with open(cjson, "wt", encoding="utf-8") as fp:
                fp.write(cjson_lua)
            MideaLogger.warning(f"Using temporary file for cjson.lua: {cjson}")

    if not os.path.exists(bit):
        from .const import BIT_LUA
        bit_lua = base64.b64decode(BIT_LUA.encode("utf-8")).decode("utf-8")
        try:
            with open(bit, "wt", encoding="utf-8") as fp:
                fp.write(bit_lua)
        except PermissionError as e:
            MideaLogger.error(f"Failed to create bit.lua at {bit}: {e}")
            # 如果无法创建文件，尝试使用临时目录
            import tempfile
            temp_dir = tempfile.gettempdir()
            bit = os.path.join(temp_dir, "bit.lua")
            with open(bit, "wt", encoding="utf-8") as fp:
                fp.write(bit_lua)
            MideaLogger.warning(f"Using temporary file for bit.lua: {bit}")

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    device_type = config_entry.data.get(CONF_TYPE)
    MideaLogger.debug(f"async_setup_entry type={device_type} data={config_entry.data}")
    if device_type == CONF_ACCOUNT:
        account = config_entry.data.get(CONF_ACCOUNT)
        password = config_entry.data.get(CONF_PASSWORD)
        server = config_entry.data.get(CONF_SERVER)

        # 初始化数据存储结构
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].setdefault("cloud_sessions", {})
        hass.data[DOMAIN].setdefault("accounts", {})
        hass.data[DOMAIN].setdefault("cloud_login_locks", {})

        # 使用账号和服务器作为会话唯一标识
        session_key = f"{account}_{server}"

        # 确保同一账号的登录操作串行执行，避免并发登录冲突
        if session_key not in hass.data[DOMAIN]["cloud_login_locks"]:
            hass.data[DOMAIN]["cloud_login_locks"][session_key] = asyncio.Lock()

        async with hass.data[DOMAIN]["cloud_login_locks"][session_key]:
            cloud = hass.data[DOMAIN]["cloud_sessions"].get(session_key)

            if not cloud:
                cloud = get_midea_cloud(
                    cloud_name=CONF_SERVERS.get(server),
                    session=async_get_clientsession(hass),
                    account=account,
                    password=password,
                )
                if not cloud or not await cloud.login():
                    MideaLogger.error("Midea cloud login failed")
                    return False
                # 缓存云会话，供其他配置条目复用
                hass.data[DOMAIN]["cloud_sessions"][session_key] = cloud
            elif not cloud._access_token:
                # 会话已存在但未登录，重新登录
                if not await cloud.login():
                    MideaLogger.error("Midea cloud login failed")
                    return False

        # 获取配置中选中的所有家庭（用于自动创建其他家庭的配置条目）
        all_selected_homes = config_entry.data.get("all_selected_homes", [])
        current_home_id = None
        selected_homes = config_entry.data.get(CONF_SELECTED_HOMES, [])
        if selected_homes:
            current_home_id = selected_homes[0]

        # 为其他选中的家庭自动创建配置条目
        if all_selected_homes and current_home_id:
            other_homes = [h for h in all_selected_homes if str(h) != str(current_home_id)]
            home_names = config_entry.data.get("home_names", {})

            for home_id in other_homes:
                home_id_str = str(home_id)
                home_name = home_names.get(home_id_str, f"家庭 {home_id}")
                # 检查该家庭是否已有配置条目
                existing_entries = hass.config_entries.async_entries(DOMAIN)
                home_exists = False
                for entry in existing_entries:
                    entry_homes = entry.data.get(CONF_SELECTED_HOMES, [])
                    if entry_homes and str(entry_homes[0]) == home_id_str:
                        home_exists = True
                        break

                if not home_exists:
                    # 异步创建该家庭的配置条目
                    hass.async_create_task(
                        hass.config_entries.flow.async_init(
                            DOMAIN,
                            context={"source": "home"},
                            data={
                                CONF_TYPE: CONF_ACCOUNT,
                                CONF_ACCOUNT: account,
                                CONF_PASSWORD: password,
                                CONF_SERVER: server,
                                CONF_SELECTED_HOMES: [home_id],
                                "home_name": home_name,
                                "home_id": home_id,
                            },
                        )
                    )

        # 拉取家庭与设备列表
        try:
            homes = await cloud.list_home()
            if homes:
                bucket = {"device_list": {}, "coordinator_map": {}}
                
                # 获取用户选择的家庭ID列表
                selected_homes = config_entry.data.get(CONF_SELECTED_HOMES, [])
                MideaLogger.debug(f"Selected homes from config: {selected_homes}")
                MideaLogger.debug(f"Available homes keys: {list(homes.keys())}")
                if not selected_homes:
                    # 如果没有选择，默认使用所有家庭
                    home_ids = list(homes.keys())
                else:
                    # 只处理用户选择的家庭，确保类型匹配
                    home_ids = []
                    for selected_home in selected_homes:
                        for key in [selected_home, str(selected_home), int(selected_home) if str(selected_home).isdigit() else None]:
                            if key is not None and key in homes and key not in home_ids:
                                home_ids.append(key)
                                break
                MideaLogger.debug(f"Final home_ids to process: {home_ids}")

                # 同步云端家庭名称到本地配置
                if home_ids:
                    home_id = home_ids[0]
                    home_info = homes.get(home_id) or homes.get(str(home_id)) or homes.get(int(home_id))
                    if home_info:
                        new_home_name = home_info.get("name", f"家庭 {home_id}") if isinstance(home_info, dict) else str(home_info) if home_info else f"家庭 {home_id}"

                        current_home_name = config_entry.data.get("home_name", "")
                        if new_home_name != current_home_name:
                            new_title = f"{account} | {new_home_name}"
                            new_data = dict(config_entry.data)
                            new_data["home_name"] = new_home_name
                            hass.config_entries.async_update_entry(
                                config_entry,
                                title=new_title,
                                data=new_data
                            )
                            MideaLogger.info(f"Updated home name from '{current_home_name}' to '{new_home_name}'")

                for home_id in home_ids:
                    appliances = await cloud.list_appliances(home_id)
                    if appliances is None:
                        continue

                    # 为每台设备构建占位设备与协调器（不连接本地）
                    for appliance_code, info in appliances.items():
                        MideaLogger.debug(f"info={info} ")

                        os.makedirs(hass.config.path(STORAGE_PATH), exist_ok=True)
                        path = hass.config.path(STORAGE_PATH)
                        file = await cloud.download_lua(
                            path=path,
                            device_type=info.get(CONF_TYPE),
                            sn=info.get(CONF_SN),
                            model_number=info.get(CONF_MODEL_NUMBER),
                            manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                        )
                        try:
                            os.makedirs(hass.config.path(STORAGE_PLUGIN_PATH), exist_ok=True)
                            plugin_path = hass.config.path(STORAGE_PLUGIN_PATH)
                            await cloud.download_plugin(
                                path=plugin_path,
                                appliance_code=appliance_code,
                                smart_product_id=info.get(CONF_SMART_PRODUCT_ID),
                                device_type=info.get(CONF_TYPE),
                                sn=info.get(CONF_SN),
                                sn8=info.get(CONF_SN8),
                                model_number=info.get(CONF_MODEL_NUMBER),
                                manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                            )
                        except Exception as e:
                            traceback.print_exc()

                        try:
                            device = MiedaDevice(
                                name=info.get(CONF_NAME),
                                device_id=appliance_code,
                                device_type=info.get(CONF_TYPE),
                                ip_address=None,
                                port=None,
                                token=None,
                                key=None,
                                connected=info.get("online"),
                                protocol=info.get(CONF_PROTOCOL) or 2,
                                model=info.get(CONF_MODEL),
                                subtype=info.get(CONF_MODEL_NUMBER),
                                manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                                sn=info.get(CONF_SN),
                                sn8=info.get(CONF_SN8),
                                lua_file=file,
                                cloud=cloud,
                            )
                            # 加载并应用设备映射（queries/centralized/calculate），并预置 attributes 键
                            try:
                                mapping = await load_device_config(
                                    hass,
                                    info.get(CONF_TYPE) or info.get("type"),
                                    info.get(CONF_SN8) or info.get("sn8"),
                                ) or {}
                            except Exception:
                                mapping = {}

                            try:
                                device.set_queries(mapping.get("queries", [{}]))
                            except Exception:
                                pass
                            try:
                                device.set_centralized(mapping.get("centralized", []))
                            except Exception:
                                pass
                            try:
                                device.set_calculate(mapping.get("calculate", {}))
                            except Exception:
                                pass

                            # 提取并设置默认值
                            try:
                                default_values = {}
                                entities_cfg = (mapping.get("entities") or {})
                                for platform_cfg in entities_cfg.values():
                                    if not isinstance(platform_cfg, dict):
                                        continue
                                    for entity_key, ecfg in platform_cfg.items():
                                        if not isinstance(ecfg, dict):
                                            continue
                                        # 检查是否有 default_value 字段
                                        if "default_value" in ecfg:
                                            # 使用 entity_key 作为属性名，或者使用 attribute 字段
                                            attr_name = ecfg.get("attribute", entity_key)
                                            default_values[attr_name] = ecfg["default_value"]
                                device.set_default_values(default_values)
                            except Exception:
                                traceback.print_exc()

                            # 预置 attributes：包含 centralized 里声明的所有键、entities 中使用到的所有属性键
                            try:
                                preset_keys = set(mapping.get("centralized", []))
                                entities_cfg = (mapping.get("entities") or {})
                                # 收集实体配置中直接引用的属性键
                                for platform_cfg in entities_cfg.values():
                                    if not isinstance(platform_cfg, dict):
                                        continue
                                    for _, ecfg in platform_cfg.items():
                                        if not isinstance(ecfg, dict):
                                            continue
                                        # 常见直接属性字段
                                        for k in [
                                            "power",
                                            "aux_heat",
                                            "current_temperature",
                                            "target_temperature",
                                            "oscillate",
                                            "min_temp",
                                            "max_temp",
                                        ]:
                                            v = ecfg.get(k)
                                            if isinstance(v, str):
                                                preset_keys.add(v)
                                            elif isinstance(v, list):
                                                for vv in v:
                                                    if isinstance(vv, str):
                                                        preset_keys.add(vv)
                                        # 模式映射里的条件字段
                                        for map_key in [
                                            "hvac_modes",
                                            "preset_modes",
                                            "swing_modes",
                                            "fan_modes",
                                            "operation_list",
                                            "options",
                                        ]:
                                            maps = ecfg.get(map_key) or {}
                                            if isinstance(maps, dict):
                                                for _, cond in maps.items():
                                                    if isinstance(cond, dict):
                                                        for attr_name in cond.keys():
                                                            preset_keys.add(attr_name)
                                # 传感器/开关等实体 key 本身也加入（其 key 即属性名）
                                for platform_name, platform_cfg in entities_cfg.items():
                                    if not isinstance(platform_cfg, dict):
                                        continue
                                    platform_str = str(platform_name)
                                    if platform_str in [
                                        str(Platform.SENSOR),
                                        str(Platform.BINARY_SENSOR),
                                        str(Platform.SWITCH),
                                        str(Platform.FAN),
                                        str(Platform.SELECT),
                                        str(Platform.VACUUM),
                                    ]:
                                        for entity_key in platform_cfg.keys():
                                            preset_keys.add(entity_key)
                                # 写入默认空值
                                for k in preset_keys:
                                    if k not in device.attributes:
                                        device.attributes[k] = None
                                # 针对T0xD9复式洗衣机，设置默认的筒选择为左筒
                                if device.device_type == 0xD9:
                                    device.attributes["db_location_selection"] = "left"
                            except Exception:
                                pass

                            coordinator = MideaDataUpdateCoordinator(hass, config_entry, device, cloud=cloud)
                            # 后台刷新，避免初始化阻塞
                            hass.async_create_task(coordinator.async_config_entry_first_refresh())
                            bucket["device_list"][appliance_code] = info
                            bucket["coordinator_map"][appliance_code] = coordinator
                        except Exception as e:
                            MideaLogger.error(f"Init device failed: {appliance_code}, error: {e}")
                    # break
                hass.data[DOMAIN]["accounts"][config_entry.entry_id] = bucket

        except Exception as e:
            MideaLogger.error(f"Fetch appliances failed: {e}")
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
        return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_type = config_entry.data.get(CONF_TYPE)
    if device_type == CONF_ACCOUNT:
        # 卸载平台并清理账号桶
        unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
        if unload_ok:
            try:
                hass.data.get(DOMAIN, {}).get("accounts", {}).pop(config_entry.entry_id, None)
            except Exception:
                pass
        return unload_ok
    if device_id is not None:
        device: MiedaDevice = hass.data[DOMAIN][DEVICES][device_id][CONF_DEVICE]
        if device is not None:
            if get_sn8_used(hass, device.sn8) == 1:
                remove_device_config(hass, device.sn8)
            # device.close()
        hass.data[DOMAIN][DEVICES].pop(device_id)
    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    return True
