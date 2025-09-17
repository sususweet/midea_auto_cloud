import os
import base64
import voluptuous as vol
from importlib import import_module
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
    ServiceCall
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
    CONF_SERVERS
)
# 账号型：登录云端、获取设备列表，并为每台设备建立协调器（无本地控制）
from .const import CONF_PASSWORD as CONF_PASSWORD_KEY, CONF_SERVER as CONF_SERVER_KEY

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    # Platform.SENSOR,
    # Platform.SWITCH,
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.WATER_HEATER,
    Platform.FAN
]


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
    if isinstance(raw, dict) and len(raw) > 0:
        # 兼容两种文件结构：
        # 1) { "<sn8>": { ...mapping... } }
        # 2) { ...mapping... }（直接就是映射体）
        if sn8 in raw:
            json_data = raw.get(sn8) or {}
        else:
            # 如果像映射体（包含 entities/centralized 等关键字段），直接使用
            if any(k in raw for k in ["entities", "centralized", "queries", "manufacturer"]):
                json_data = raw
    if not json_data:
        device_path = f".device_mapping.{'T0x%02X' % device_type}"
        try:
            mapping_module = import_module(device_path, __package__)
            if sn8 in mapping_module.DEVICE_MAPPING.keys():
                json_data = mapping_module.DEVICE_MAPPING[sn8]
            elif "default" in mapping_module.DEVICE_MAPPING:
                json_data = mapping_module.DEVICE_MAPPING["default"]
            if len(json_data) > 0:
                save_data = {sn8: json_data}
                # offload save_json as well
                await hass.async_add_executor_job(save_json, config_file, save_data)
        except ModuleNotFoundError:
            MideaLogger.warning(f"Can't load mapping file for type {'T0x%02X' % device_type}")
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
    cjson = os.getcwd() + "/cjson.lua"
    bit = os.getcwd() + "/bit.lua"
    if not os.path.exists(cjson):
        from .const import CJSON_LUA
        cjson_lua = base64.b64decode(CJSON_LUA.encode("utf-8")).decode("utf-8")
        with open(cjson, "wt") as fp:
            fp.write(cjson_lua)
    if not os.path.exists(bit):
        from .const import BIT_LUA
        bit_lua = base64.b64decode(BIT_LUA.encode("utf-8")).decode("utf-8")
        with open(bit, "wt") as fp:
            fp.write(bit_lua)
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    device_type = config_entry.data.get(CONF_TYPE)
    MideaLogger.debug(f"async_setup_entry type={device_type} data={config_entry.data}")
    if device_type == CONF_ACCOUNT:
        account = config_entry.data.get(CONF_ACCOUNT)
        password = config_entry.data.get(CONF_PASSWORD_KEY)
        server = config_entry.data.get(CONF_SERVER_KEY)
        cloud_name = CONF_SERVERS.get(server)
        cloud = get_midea_cloud(
            cloud_name=cloud_name,
            session=async_get_clientsession(hass),
            account=account,
            password=password,
        )
        if not cloud or not await cloud.login():
            MideaLogger.error("Midea cloud login failed")
            return False

        # 拉取家庭与设备列表
        appliances = None
        first_home_id = None
        try:
            homes = await cloud.list_home()
            if homes and len(homes) > 0:
                first_home_id = list(homes.keys())[0]
                appliances = await cloud.list_appliances(first_home_id)
            else:
                appliances = await cloud.list_appliances(None)
        except Exception as e:
            MideaLogger.error(f"Fetch appliances failed: {e}")
            appliances = None

        if appliances is None:
            appliances = {}

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].setdefault("accounts", {})
        bucket = {"device_list": {}, "coordinator_map": {}, "cloud": cloud, "home_id": first_home_id}

        # 为每台设备构建占位设备与协调器（不连接本地）
        for appliance_code, info in appliances.items():
            MideaLogger.debug(f"info={info} ")
            try:
                device = MiedaDevice(
                    name=info.get(CONF_NAME) or info.get("name"),
                    device_id=appliance_code,
                    device_type=info.get(CONF_TYPE) or info.get("type"),
                    ip_address=None,
                    port=None,
                    token=None,
                    key=None,
                    connected=info.get("online"),
                    protocol=info.get(CONF_PROTOCOL) or 2,
                    model=info.get(CONF_MODEL),
                    subtype=info.get(CONF_MODEL_NUMBER),
                    sn=info.get(CONF_SN) or info.get("sn"),
                    sn8=info.get(CONF_SN8) or info.get("sn8"),
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
                    device.set_queries(mapping.get("queries", []))
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
                        ]:
                            for entity_key in platform_cfg.keys():
                                preset_keys.add(entity_key)
                    # 写入默认空值
                    for k in preset_keys:
                        if k not in device.attributes:
                            device.attributes[k] = None
                except Exception:
                    pass

                coordinator = MideaDataUpdateCoordinator(hass, config_entry, device)
                await coordinator.async_config_entry_first_refresh()
                bucket["device_list"][appliance_code] = info
                bucket["coordinator_map"][appliance_code] = coordinator
            except Exception as e:
                MideaLogger.error(f"Init device failed: {appliance_code}, error: {e}")

        hass.data[DOMAIN]["accounts"][config_entry.entry_id] = bucket

        hass.async_create_task(hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS))
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
