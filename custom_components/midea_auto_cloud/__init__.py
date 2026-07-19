import asyncio
import json
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
from .core import session_store
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
    CONF_PASSWORD, CONF_SERVER,
    CONF_CATEGORY,
)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TIME,
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.BUTTON,
    Platform.WATER_HEATER,
    Platform.FAN,
    Platform.LIGHT,
    Platform.HUMIDIFIER,
    Platform.NUMBER,
    Platform.VACUUM,
    Platform.COVER,
    Platform.TEXT,
    Platform.LOCK,
]


async def import_module_async(name: str):
    return await asyncio.to_thread(import_module, name, __package__)


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


def get_device_mapping(
        device_mappings: dict,
        device_type: int,
        sn8: str = "",
        subtype: int | None = None,
        category: str | None = None,
) -> dict:
    """按 subtype -> sn8 -> default_category -> default 的优先级选择映射。"""
    # 没有任何映射直接返回空
    if not device_mappings:
        return {}

    result = None

    # 1. 优先按 subtype 精确匹配：("subtype", "1234") 或 ("subtype", 1234)
    if subtype is not None:
        subtype_str = str(subtype)
        for key, config in device_mappings.items():
            if (
                    isinstance(key, tuple)
                    and len(key) == 2
                    and key[0] == "subtype"
                    and str(key[1]) == subtype_str
            ):
                result = config
                break

    # 2. 如果还没匹配到，再按 sn8 规则匹配
    if result is None and sn8:
        for key, config in device_mappings.items():
            # 直接等于 / tuple 包含 / 正则匹配
            if (
                    key == sn8
                    or (isinstance(key, tuple) and sn8 in key)
                    or (isinstance(key, str) and re.match(key, sn8))
            ):
                result = config
                break

    # 3. 如果依然没有，且有 category，则尝试 default_{category}
    if result is None and category:
        category_key = f"default_{category.replace('-', '_')}"
        if category_key in device_mappings:
            result = device_mappings[category_key]

    # 4. 再尝试通用 default
    if result is None and "default" in device_mappings:
        result = device_mappings["default"]

    if not result:
        MideaLogger.warning(
            f"No mapping found for sn8 {sn8} subtype {subtype} category {category} in type {'T0x%02X' % device_type}"
        )

    # ── Build default _mode_features from DEVICE_MAPPING superset ──
    # When cloud is unavailable, we still need mode_features so that
    # mode_dependent entities behave correctly.  Without this, the
    # empty dict {} is falsy → all mode_dependent entities appear
    # available (the "superset" problem the user sees).
    if result and not result.get("_mode_features"):
        from .const import Platform
        entities = result.get("entities", {})
        selects = entities.get(Platform.SELECT, {})
        wm = selects.get("wash_mode", {})
        opts = wm.get("options", {}) if isinstance(wm, dict) else {}
        all_features = []
        for sel_key, sel_cfg in selects.items():
            if isinstance(sel_cfg, dict) and sel_cfg.get("mode_dependent"):
                all_features.append(sel_key)
        if all_features and opts:
            result["_mode_features"] = {m: all_features for m in opts}
        else:
            result["_mode_features"] = {}

    return result


def _home_display_name(home_info, home_id) -> str:
    if isinstance(home_info, dict):
        return home_info.get("name") or home_info.get("homeName") or f"家庭 {home_id}"
    return str(home_info) if home_info else f"家庭 {home_id}"


def _match_home_ids(selected_homes: list, homes: dict) -> list:
    home_ids = []
    for selected_home in selected_homes:
        for key in (
            selected_home,
            str(selected_home),
            int(selected_home) if str(selected_home).isdigit() else None,
        ):
            if key is not None and key in homes and key not in home_ids:
                home_ids.append(key)
                break
    return home_ids


def _resolve_home_ids(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    selected_homes: list,
    homes: dict,
) -> list:
    """Resolve configured home ids against the live cloud home list.

    Older releases could persist placeholder ids (e.g. ``1``) when the cloud
    API was unavailable during setup. Recover by name, sole-home fallback, or
    all-homes fallback, then migrate the config entry to real homegroup ids.
    """
    if not homes:
        return []
    if not selected_homes:
        return list(homes.keys())

    home_ids = _match_home_ids(selected_homes, homes)
    if home_ids:
        return home_ids

    configured_name = config_entry.data.get("home_name", "")
    if configured_name:
        for hid, info in homes.items():
            if _home_display_name(info, hid) == configured_name:
                home_ids = [hid]
                break

    if not home_ids:
        for name in config_entry.data.get("home_names", {}).values():
            for hid, info in homes.items():
                if _home_display_name(info, hid) == name and hid not in home_ids:
                    home_ids.append(hid)

    if not home_ids and len(homes) == 1:
        home_ids = list(homes.keys())
        MideaLogger.warning(
            f"Configured home id(s) {selected_homes} not found; "
            f"using sole available home {home_ids[0]}"
        )

    if not home_ids:
        MideaLogger.warning(
            f"Configured home id(s) {selected_homes} not found in {list(homes.keys())}; "
            f"falling back to all available homes"
        )
        home_ids = list(homes.keys())

    if home_ids and not _match_home_ids(selected_homes, homes):
        new_data = dict(config_entry.data)
        new_data[CONF_SELECTED_HOMES] = [home_ids[0]]
        new_data["all_selected_homes"] = home_ids
        new_data["home_names"] = {
            str(hid): _home_display_name(homes[hid], hid) for hid in home_ids
        }
        new_data["home_name"] = new_data["home_names"][str(home_ids[0])]
        title_prefix = config_entry.data.get(CONF_ACCOUNT, "")
        if " | " in config_entry.title:
            title_prefix = config_entry.title.split(" | ", 1)[0]
        hass.config_entries.async_update_entry(
            config_entry,
            title=f"{title_prefix} | {new_data['home_name']}",
            data=new_data,
        )
        MideaLogger.info(
            f"Migrated stale home ids {selected_homes} to {home_ids}"
        )

    return home_ids


async def _ensure_msmart_home_api_route(cloud) -> None:
    """Re-resolve MSmartHome regional API URL after restoring a cached session."""
    re_route = getattr(cloud, "_re_route", None)
    if re_route is not None:
        await re_route()


async def load_device_config(hass: HomeAssistant, device_type, sn8, subtype=None, category=None, cloud=None):
    """Load per-device mapping, optionally enhanced with cloud config and diff."""
    json_data = {}

    device_path = f".device_mapping.{'T0x%02X' % device_type}"
    try:
        mapping_module = await import_module_async(device_path)
        device_mappings = getattr(mapping_module, "DEVICE_MAPPING", {}) or {}
        json_data = get_device_mapping(
            device_mappings=device_mappings,
            device_type=device_type,
            sn8=sn8,
            subtype=subtype,
            category=category,
        )
    except ModuleNotFoundError:
        MideaLogger.warning(
            f"Can't load mapping file for type {'T0x%02X' % device_type}. "
            f"sn8: {sn8}, subtype: {subtype}, category: {category}. "
        )

    # ── Download cloud config for auto-adaptation ──
    if cloud is not None and sn8 and device_type:
        try:
            config_dir = hass.config.path(CONFIG_PATH)
            os.makedirs(config_dir, exist_ok=True)
            config_file = hass.config.path(f"{CONFIG_PATH}/{sn8}_config.json")
            diff_file = hass.config.path(f"{CONFIG_PATH}/T0x{device_type:02X}_diff.json")

            # Load or download device config (async file I/O)
            device_config = None
            if os.path.exists(config_file):
                def _read_device_config():
                    with open(config_file, encoding="utf-8") as f:
                        return json.loads(f.read())
                try:
                    device_config = await hass.async_add_executor_job(_read_device_config)
                except (json.JSONDecodeError, OSError):
                    pass
            if not device_config:
                device_config = await cloud.download_device_config(sn8, device_type)
                if device_config:
                    def _write_device_config():
                        with open(config_file, "w", encoding="utf-8") as f:
                            json.dump(device_config, f, ensure_ascii=False)
                    await hass.async_add_executor_job(_write_device_config)
                    MideaLogger.info(f"Downloaded device config for SN8={sn8}")

            # Load or download diff config (async file I/O)
            diff_config = None
            if os.path.exists(diff_file):
                def _read_diff_config():
                    with open(diff_file, encoding="utf-8") as f:
                        return json.loads(f.read())
                try:
                    diff_config = await hass.async_add_executor_job(_read_diff_config)
                except (json.JSONDecodeError, OSError):
                    pass
            if not diff_config:
                diff_config = await cloud.download_diff_config(device_type)
                if diff_config:
                    def _write_diff_config():
                        with open(diff_file, "w", encoding="utf-8") as f:
                            json.dump(diff_config, f, ensure_ascii=False)
                    await hass.async_add_executor_job(_write_diff_config)
                    MideaLogger.info(f"Downloaded diff config for type 0x{device_type:02X}")

            # Apply device config (currently only E1 supports cloud config merging)
            if device_config and device_type == 0xE1:
                try:
                    from .device_mapping.T0xE1 import apply_device_config
                    json_data = apply_device_config(
                        json_data, device_config, device_type, 0
                    )
                    MideaLogger.info(
                        f"Applied cloud config for SN8={sn8}, type=0x{device_type:02X}"
                    )
                except Exception as e:
                    MideaLogger.warning(f"Failed to apply device config: {e}")

            # Compute diff_flags: cloud-first, local fallback (matching mini-program).
            fallback_diff = None
            if device_type == 0xE1 and not diff_config:
                try:
                    from .device_mapping.T0xE1 import get_default_diff
                    fallback_diff = get_default_diff()
                except ImportError:
                    pass
            if diff_config:
                json_data["_diff_config"] = diff_config
            diff_flags = _compute_diff_flags(diff_config, sn8, fallback_diff)
            json_data["_diff_flags"] = diff_flags
            active = {k: v for k, v in diff_flags.items() if v}
            if active:
                source = "cloud" if diff_config else "fallback"
                MideaLogger.info(f"Diff flags ({source}) for SN8={sn8}: {active}")

            # withoutOrder: hide order entities
            if json_data.get("_diff_flags", {}).get("withoutOrder"):
                entities_cfg = json_data.get("entities", {})
                entities_cfg.get(Platform.TIME, {}).pop("order_set_time", None)
                entities_cfg.get(Platform.SENSOR, {}).pop("order_left_time", None)
                entities_cfg.get(Platform.BUTTON, {}).pop("start_order", None)
                MideaLogger.info(f"Device {sn8} does not support order — hiding order entities")

        except Exception as e:
            MideaLogger.warning(f"Cloud config download failed, using static mapping: {e}")

    # Compute order_left_total for E1 devices
    if device_type == 0xE1:
        json_data = _add_order_left_total(json_data)

    # Merge cloud statistics sensors
    json_data = _apply_cloud_stats(json_data, device_type)

    return json_data


def _compute_diff_flags(diff_config: dict, sn8: str, fallback: dict = None) -> dict[str, bool]:
    """Pre-compute diff flags: cloud-first, local fallback (matching mini-program)."""
    result: dict[str, bool] = {}
    source = diff_config if (diff_config and sn8) else fallback
    if source:
        for category, sn8_list in source.get("diffType", {}).items():
            result[category] = sn8 in sn8_list
    return result


def _add_order_left_total(mapping: dict) -> dict:
    """Add order_left_total calculated sensor attribute for E1 devices.

    The cloud API returns order_left_hour and order_left_min separately.
    This adds a calculate expression to combine them into total minutes.
    """
    import copy
    result = copy.deepcopy(mapping)
    calculate = dict(result.get("calculate") or {})
    calc_get = list(calculate.get("get") or [])
    calc_get.append({
        "lvalue": "[order_left_total]",
        "rvalue": "[order_left_min] + 60 * [order_left_hour]"
    })
    calculate["get"] = calc_get
    result["calculate"] = calculate
    return result


def _apply_cloud_stats(mapping: dict, device_type: int) -> dict:
    """Merge cloud statistics sensors (water/electricity)."""
    try:
        from .device_mapping._cloud_stats import merge_cloud_stats_mapping
    except ImportError:
        return mapping
    return merge_cloud_stats_mapping(mapping, device_type)


def _install_e1_coordinator_attrs(coordinator, mapping: dict, device_type=0) -> None:
    """Store E1-specific config on coordinator for entity access."""
    coordinator._device_mapping = mapping
    coordinator._diff_flags = mapping.get("_diff_flags", {})
    coordinator._keep_start_now = mapping.get("_keep_start_now", False)
    coordinator._keep_time_type = mapping.get("_keep_time_type", 0)
    coordinator._keep_text_name = mapping.get("_keep_text_name", "")
    coordinator._dry_text_name = mapping.get("_dry_text_name", "")
    coordinator._mode_features = mapping.get("_mode_features", {})
    coordinator._missing_features = set(mapping.get("_missing_features", []))
    coordinator._device_mapping_entities = mapping.get("entities", {})
    MideaLogger.debug(
        f"E1 coordinator attrs: keep_start_now={coordinator._keep_start_now}, "
        f"diff_flags={list(k for k, v in coordinator._diff_flags.items() if v) if coordinator._diff_flags else 'none'}"
    )


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


def _write_lua_support_file(path: str, content: str) -> None:
    with open(path, "wt", encoding="utf-8") as fp:
        fp.write(content)


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
            await hass.async_add_executor_job(_write_lua_support_file, cjson, cjson_lua)
        except PermissionError as e:
            MideaLogger.error(f"Failed to create cjson.lua at {cjson}: {e}")
            # 如果无法创建文件，尝试使用临时目录
            import tempfile
            temp_dir = tempfile.gettempdir()
            cjson = os.path.join(temp_dir, "cjson.lua")
            await hass.async_add_executor_job(_write_lua_support_file, cjson, cjson_lua)
            MideaLogger.warning(f"Using temporary file for cjson.lua: {cjson}")

    if not os.path.exists(bit):
        from .const import BIT_LUA
        bit_lua = base64.b64decode(BIT_LUA.encode("utf-8")).decode("utf-8")
        try:
            await hass.async_add_executor_job(_write_lua_support_file, bit, bit_lua)
        except PermissionError as e:
            MideaLogger.error(f"Failed to create bit.lua at {bit}: {e}")
            # 如果无法创建文件，尝试使用临时目录
            import tempfile
            temp_dir = tempfile.gettempdir()
            bit = os.path.join(temp_dir, "bit.lua")
            await hass.async_add_executor_job(_write_lua_support_file, bit, bit_lua)
            MideaLogger.warning(f"Using temporary file for bit.lua: {bit}")

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    device_type = config_entry.data.get(CONF_TYPE)
    MideaLogger.debug(f"async_setup_entry type={device_type} data={config_entry.data}")
    if device_type == CONF_ACCOUNT:
        account = config_entry.data.get(CONF_ACCOUNT)
        password = config_entry.data.get(CONF_PASSWORD)
        server = config_entry.data.get(CONF_SERVER)

        # 统一 server 类型，避免同一 server 因类型差异产生不同 session_key
        try:
            server = int(server)
        except Exception:
            pass

        # 初始化数据存储结构
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].setdefault("cloud_sessions", {})
        hass.data[DOMAIN].setdefault("accounts", {})
        hass.data[DOMAIN].setdefault("cloud_login_locks", {})

        # 使用账号和服务器作为会话唯一标识
        session_key = session_store.build_session_key(account, server)

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
                if cloud:
                    cloud.set_login_success_callback(
                        lambda c, _h=hass, _a=account, _p=password, _s=server: session_store.async_persist_cloud_session(_h, c, _a, _p, _s)
                    )
                    if await session_store.async_restore_cloud_session(hass, cloud, account, password, server):
                        await _ensure_msmart_home_api_route(cloud)
                    elif not await cloud.login():
                        MideaLogger.error("Midea cloud login failed")
                        return False
                else:
                    MideaLogger.error("Midea cloud login failed")
                    return False
                # 缓存云会话，供其他配置条目复用
                hass.data[DOMAIN]["cloud_sessions"][session_key] = cloud
            elif not cloud._access_token:
                # 会话已存在但未登录，重新登录
                cloud.set_login_success_callback(
                    lambda c, _h=hass, _a=account, _p=password, _s=server: session_store.async_persist_cloud_session(_h, c, _a, _p, _s)
                )
                if await session_store.async_restore_cloud_session(hass, cloud, account, password, server):
                    await _ensure_msmart_home_api_route(cloud)
                elif not await cloud.login():
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
                    # 获取该家庭的设备数量
                    appliances = await cloud.list_appliances(home_id)
                    device_count = len(appliances or [])
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
                                "nickname": cloud.nickname,
                                "device_count": device_count,
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
                MideaLogger.debug(
                    f"Selected homes from config: {selected_homes}, Available homes keys: {list(homes.keys())}")
                home_ids = _resolve_home_ids(hass, config_entry, selected_homes, homes)
                MideaLogger.debug(f"Final home_ids to process: {home_ids}")

                # 同步云端家庭名称到本地配置
                if home_ids:
                    home_id = home_ids[0]
                    home_info = homes.get(home_id) or homes.get(str(home_id)) or homes.get(int(home_id))
                    if home_info:
                        new_home_name = home_info.get("name", f"家庭 {home_id}") if isinstance(home_info,
                                                                                               dict) else str(
                            home_info) if home_info else f"家庭 {home_id}"
                        current_home_name = config_entry.data.get("home_name", "")
                        if new_home_name != current_home_name:
                            new_title = f"{cloud.nickname} | {new_home_name}"
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
                        file = None

                        try:
                            file = await cloud.download_lua(
                                path=path,
                                device_type=info.get(CONF_TYPE),
                                sn=info.get(CONF_SN),
                                model_number=info.get(CONF_MODEL_NUMBER),
                                manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                                smart_product_id=info.get(CONF_SMART_PRODUCT_ID),
                            )
                        except Exception as e:
                            MideaLogger.warning(f"Failed to download lua for {info.get(CONF_NAME)}: {e}")

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
                            MideaLogger.warning(f"Failed to download plugin for {info.get(CONF_NAME)}: {e}")

                        try:
                            device = MiedaDevice(
                                name=info.get(CONF_NAME),
                                device_id=appliance_code,
                                device_type=info.get(CONF_TYPE),
                                ip_address=None,
                                port=None,
                                token=None,
                                key=None,
                                connected=info.get("online", True),
                                protocol=info.get(CONF_PROTOCOL) or 2,
                                model=info.get(CONF_MODEL),
                                subtype=info.get(CONF_MODEL_NUMBER),
                                manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                                category=info.get(CONF_CATEGORY),
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
                                    device.subtype,
                                    device.category,
                                    cloud=cloud,
                                ) or {}
                            except Exception:
                                mapping = {}

                            try:
                                device.set_queries(mapping.get("queries", [{}]))
                            except Exception:
                                pass
                            try:
                                device.set_cloud_queries(mapping.get("cloud_queries", {}))
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
                                        str(Platform.LOCK),
                                        str(Platform.TEXT),
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
                            # Store E1-specific config on coordinator
                            if info.get("type") == 0xE1:
                                _install_e1_coordinator_attrs(coordinator, mapping, device_type=info.get("type"))
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
