import os
import traceback
import lupa
import threading
import json
from .logger import MideaLogger


class LuaRuntime:
    def __init__(self, file):
        self._runtimes = lupa.lua51.LuaRuntime()

        # 设置Lua路径，包含cjson.lua和bit.lua的目录
        lua_dir = os.path.dirname(os.path.abspath(file))
        self._runtimes.execute(f'package.path = package.path .. ";{lua_dir}/?.lua"')

        # 加载必需的Lua库
        try:
            self._runtimes.execute('require "cjson"')
        except Exception as e:
            MideaLogger.warning(f"Failed to load cjson: {e}")
        
        try:
            self._runtimes.execute('require "bit"')
        except Exception as e:
            MideaLogger.warning(f"Failed to load bit: {e}")
        
        # 加载设备特定的Lua文件
        string = f'dofile("{file}")'
        self._runtimes.execute(string)
        self._lock = threading.Lock()
        self._json_to_data = self._runtimes.eval("function(param) return jsonToData(param) end")
        self._data_to_json = self._runtimes.eval("function(param) return dataToJson(param) end")

    def json_to_data(self, json_value):
        with self._lock:
            result = self._json_to_data(json_value)

        return result

    def data_to_json(self, data_value):
        with self._lock:
            result = self._data_to_json(data_value)
        return result


class MideaCodec(LuaRuntime):
    def __init__(self, file, device_type=None, sn=None, subtype=None):
        super().__init__(file)
        self._device_type = device_type
        self._sn = sn
        self._subtype = subtype

    def _build_base_dict(self):
        device_info ={}
        if self._sn is not None:
            device_info["deviceSN"] = self._sn
        if self._subtype is not None:
            device_info["deviceSubType"] = self._subtype
        base_dict = {
            "deviceinfo": device_info
        }
        return base_dict

    def build_query(self, append=None):
        query_dict = self._build_base_dict()
        query_dict["query"] = {} if append is None else append
        json_str = json.dumps(query_dict)
        try:
            result = self.json_to_data(json_str)
            return result
        except lupa.LuaError as e:
            MideaLogger.error(f"LuaRuntimeError in build_query {json_str}: {repr(e)}")
        return None

    def build_control(self, append=None, status=None):
        query_dict = self._build_base_dict()
        query_dict["control"] = {} if append is None else append
        query_dict["status"] = {} if status is None else status
        # 针对T0xD9复式洗衣机特殊处理
        if self._device_type == "T0xD9":
            control_keys = list(append.keys())
            if len(control_keys) > 0:
                # 从第一个键名中提取前缀，例如从 'db_power' 中提取 'db'
                first_key = control_keys[0]
                prefix = first_key.split("_")[0]
                query_dict["control"]["bucket"] = prefix
            else:
                query_dict["control"]["bucket"] = "db"
        json_str = json.dumps(query_dict)
        MideaLogger.debug(f"LuaRuntime json_str {json_str}")
        try:
            result = self.json_to_data(json_str)
            MideaLogger.debug(f"LuaRuntime Result {result}")
            return result
        except lupa.LuaError as e:
            traceback.print_exc()
            MideaLogger.error(f"LuaRuntimeError in build_control {json_str}: {repr(e)}")
            return None

    def build_status(self, append=None):
        query_dict = self._build_base_dict()
        query_dict["status"] = {} if append is None else append
        json_str = json.dumps(query_dict)
        try:
            result = self.json_to_data(json_str)
            return result
        except lupa.LuaError as e:
            MideaLogger.error(f"LuaRuntimeError in build_status {json_str}: {repr(e)}")
            return None

    def decode_status(self, data: str):
        data_dict = self._build_base_dict()
        data_dict["msg"] = {
            "data": data
        }
        json_str = json.dumps(data_dict)
        try:
            result = self.data_to_json(json_str)
            status = json.loads(result)
            return status.get("status")
        except lupa.LuaError as e:
            MideaLogger.error(f"LuaRuntimeError in decode_status {data}: {repr(e)}")
        return None

