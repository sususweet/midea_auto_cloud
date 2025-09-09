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
    CONF_LUA_FILE
)

ALL_PLATFORM = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
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


def load_device_config(hass: HomeAssistant, device_type, sn8):
    os.makedirs(hass.config.path(CONFIG_PATH), exist_ok=True)
    config_file = hass.config.path(f"{CONFIG_PATH}/{sn8}.json")
    json_data = load_json(config_file, default={})
    if len(json_data) > 0:
        json_data = json_data.get(sn8)
    else:
        device_path = f".device_mapping.{'T0x%02X' % device_type}"
        try:
            mapping_module = import_module(device_path, __package__)
            if sn8 in mapping_module.DEVICE_MAPPING.keys():
                json_data = mapping_module.DEVICE_MAPPING[sn8]
            elif "default" in mapping_module.DEVICE_MAPPING:
                json_data = mapping_module.DEVICE_MAPPING["default"]
            if len(json_data) > 0:
                save_data = {sn8: json_data}
                save_json(config_file, save_data)
        except ModuleNotFoundError:
            MideaLogger.warning(f"Can't load mapping file for type {'T0x%02X' % device_type}")
    return json_data


def register_services(hass: HomeAssistant):

    async def async_set_attributes(service: ServiceCall):
        device_id = service.data.get("device_id")
        attributes = service.data.get("attributes")
        MideaLogger.debug(f"Service called: set_attributes, device_id: {device_id}, attributes: {attributes}")
        try:
            coordinator: MideaDataUpdateCoordinator = hass.data[DOMAIN][DEVICES][device_id].get("coordinator")
        except KeyError:
            MideaLogger.error(f"Failed to call service set_attributes: the device {device_id} isn't exist.")
            return
        if coordinator:
            await coordinator.async_set_attributes(attributes)

    async def async_send_command(service: ServiceCall):
        device_id = service.data.get("device_id")
        cmd_type = service.data.get("cmd_type")
        cmd_body = service.data.get("cmd_body")
        try:
            coordinator: MideaDataUpdateCoordinator = hass.data[DOMAIN][DEVICES][device_id].get("coordinator")
        except KeyError:
            MideaLogger.error(f"Failed to call service send_command: the device {device_id} isn't exist.")
            return
        if coordinator:
            await coordinator.async_send_command(cmd_type, cmd_body)

    hass.services.async_register(
        DOMAIN, 
        "set_attributes", 
        async_set_attributes,
        schema=vol.Schema({ 
            vol.Required("device_id"): vol.Coerce(int),
            vol.Required("attributes"): vol.Any(dict)
        })
    )
    hass.services.async_register(
        DOMAIN, "send_command", async_send_command,
        schema=vol.Schema({
            vol.Required("device_id"): vol.Coerce(int),
            vol.Required("cmd_type"): vol.In([2, 3]),
            vol.Required("cmd_body"): str
        })
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

    register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    device_type = config_entry.data.get(CONF_TYPE)
    if device_type == CONF_ACCOUNT:
        return True
    name = config_entry.data.get(CONF_NAME)
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_type = config_entry.data.get(CONF_TYPE)
    token = config_entry.data.get(CONF_TOKEN)
    key = config_entry.data.get(CONF_KEY)
    ip_address = config_entry.options.get(CONF_IP_ADDRESS, None)
    if not ip_address:
        ip_address = config_entry.data.get(CONF_IP_ADDRESS)
    refresh_interval = config_entry.options.get(CONF_REFRESH_INTERVAL)
    port = config_entry.data.get(CONF_PORT)
    model = config_entry.data.get(CONF_MODEL)
    protocol = config_entry.data.get(CONF_PROTOCOL)
    subtype = config_entry.data.get(CONF_MODEL_NUMBER)
    sn = config_entry.data.get(CONF_SN)
    sn8 = config_entry.data.get(CONF_SN8)
    lua_file = config_entry.data.get(CONF_LUA_FILE)
    if protocol == 3 and (key is None or key is None):
        MideaLogger.error("For V3 devices, the key and the token is required.")
        return False
    device = MiedaDevice(
        name=name,
        device_id=device_id,
        device_type=device_type,
        ip_address=ip_address,
        port=port,
        token=token,
        key=key,
        protocol=protocol,
        model=model,
        subtype=subtype,
        sn=sn,
        sn8=sn8,
        lua_file=lua_file,
    )
    if refresh_interval is not None:
        device.set_refresh_interval(refresh_interval)
    device.open()
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if DEVICES not in hass.data[DOMAIN]:
        hass.data[DOMAIN][DEVICES] = {}
    
    # Create data coordinator
    coordinator = MideaDataUpdateCoordinator(hass, config_entry, device)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][DEVICES][device_id] = {}
    hass.data[DOMAIN][DEVICES][device_id][CONF_DEVICE] = device
    hass.data[DOMAIN][DEVICES][device_id]["coordinator"] = coordinator
    hass.data[DOMAIN][DEVICES][device_id][CONF_ENTITIES] = {}
    
    config = load_device_config(hass, device_type, sn8)
    if config is not None and len(config) > 0:
        queries = config.get("queries")
        if queries is not None and isinstance(queries, list):
            device.set_queries(queries)
        centralized = config.get("centralized")
        if centralized is not None and isinstance(centralized, list):
            device.set_centralized(centralized)
        calculate = config.get("calculate")
        if calculate is not None and isinstance(calculate, dict):
            device.set_calculate(calculate)
        hass.data[DOMAIN][DEVICES][device_id]["manufacturer"] = config.get("manufacturer")
        hass.data[DOMAIN][DEVICES][device_id]["rationale"] = config.get("rationale")
        hass.data[DOMAIN][DEVICES][device_id][CONF_ENTITIES] = config.get(CONF_ENTITIES)
    
    for platform in ALL_PLATFORM:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(
            config_entry, platform))
    config_entry.add_update_listener(update_listener)
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    if device_id is not None:
        device: MiedaDevice = hass.data[DOMAIN][DEVICES][device_id][CONF_DEVICE]
        if device is not None:
            if get_sn8_used(hass, device.sn8) == 1:
                lua_file = config_entry.data.get("lua_file")
                os.remove(lua_file)
                remove_device_config(hass, device.sn8)
            device.close()
        hass.data[DOMAIN][DEVICES].pop(device_id)
    for platform in ALL_PLATFORM:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    return True
