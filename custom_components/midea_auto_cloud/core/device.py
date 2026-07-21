import threading
import socket
import traceback
import re
from enum import IntEnum

from .cloud import MideaCloud, MSmartHomeCloud, MeijuCloud
from .security import LocalSecurity, MSGTYPE_HANDSHAKE_REQUEST, MSGTYPE_ENCRYPTED_REQUEST
from .packet_builder import PacketBuilder
from .message import MessageQuestCustom
from .logger import MideaLogger
from .lua_runtime import MideaCodec
from .util import dec_string_to_bytes


class AuthException(Exception):
    pass


class ResponseException(Exception):
    pass


class RefreshFailed(Exception):
    pass


class ParseMessageResult(IntEnum):
    SUCCESS = 0
    PADDING = 1
    ERROR = 99


LAMP_CONTROL_KEYS = frozenset({
    "lamp_control1_power",
    "lamp_control2_power",
    "lamp_control3_power",
})

# E3 newCtrlAgreementJsonToCmd(status) runs before control; these fields reuse
# cmd[12]/cmd[13] and corrupt lamp_control (0x21) when temperature=39 -> 0x27.
LAMP_CONTROL_STATUS_EXCLUDE = frozenset({
    "temperature",
    "temperature_beep",
})


class MiedaDevice(threading.Thread):
    def __init__(self,
                 name: str,
                 device_id: int,
                 device_type: int,
                 ip_address: str | None,
                 port: int | None,
                 token: str | None,
                 key: str | None,
                 protocol: int,
                 model: str | None,
                 subtype: int | None,
                 manufacturer_code: str | None,
                 category: str | None,
                 connected: bool,
                 sn: str | None,
                 sn8: str | None,
                 lua_file: str | None,
                 cloud: MideaCloud | None):
        threading.Thread.__init__(self)
        self._socket = None
        self._ip_address = ip_address
        self._port = port
        self._security = LocalSecurity()
        self._token = bytes.fromhex(token) if token else None
        self._key = bytes.fromhex(key) if key else None
        self._buffer = b""
        self._device_name = name
        self._device_id = device_id
        self._device_type = device_type
        self._protocol = protocol
        self._model = model
        self._updates = []
        self._is_run = False
        self._subtype = subtype
        self._sn = sn
        self._sn8 = sn8
        self._manufacturer_code = manufacturer_code
        self._category = category
        self._attributes = {
            "device_type": "T0x%02X" % device_type,
            "sn": sn,
            "sn8": sn8,
            "subtype": subtype,
            "category": category,
        }
        self._refresh_interval = 20
        self._heartbeat_interval = 10
        self._device_connected(connected)
        self._queries = [{}]
        # 云端返回 lua analysis exception (1014) 的查询，后续刷新不再重试
        self._skipped_queries: set = set()
        self._cloud_queries = {}
        self._centralized = []
        self._calculate_get = []
        self._calculate_set = []
        self._default_values = {}
        self._lua_runtime = MideaCodec(lua_file, device_type=self._attributes.get("device_type"), sn=sn, subtype=subtype) if lua_file is not None else None
        self._cloud = cloud

    def _handle_t0xd9_db_location_selection(self, status, value):
        # 处理T0xD9复式洗衣机的db_location_selection更新
        if value == "left":
            status["db_location"] = 1
            self._attributes["db_location"] = 1
        elif value == "right":
            status["db_location"] = 2
            self._attributes["db_location"] = 2

    def _adjust_t0xd9_db_location_based_on_position(self, status=None):
        # 根据db_position调整T0xD9复式洗衣机的db_location
        db_position = self._attributes.get("db_position", 1)
        current_location = self._attributes.get("db_location", 1)
        
        if db_position == 1:
            # db_position = 1，db_location 保持不变
            calculated_location = current_location
        elif db_position == 0:
            # db_position = 0，db_location 切换为另一个选项
            calculated_location = 2 if current_location == 1 else 1
        
        if status is not None:
            status["db_location"] = calculated_location
        
        return calculated_location

    def _sync_t0xd9_location_selection(self, location):
        # 同步T0xD9复式洗衣机的db_location和db_location_selection
        if location == 1:
            self._attributes["db_location_selection"] = "left"
        elif location == 2:
            self._attributes["db_location_selection"] = "right"

    def _adjust_control_status(self, running_status):
        # 依据运行状态调整设备的控制状态
        # 根据运行状态确定控制状态, 只有当运行状态是"start"时，控制状态才为"start"
        if running_status == "start":
            control_status = "start"
        # 其他所有情况(包括standby、pause、off、error等)，控制状态应为pause
        else:
            control_status = "pause"
        
        # 根据设备类型确定控制状态属性名
        if self._device_type == 0xD9:
            # T0xD9复式洗衣机使用db_control_status
            control_status_key = "db_control_status"
        elif self._device_type in [0xDA, 0xDB, 0xDC]:
            # T0xDA、T0xDB、T0xDC设备使用control_status
            control_status_key = "control_status"
        else:
            # 默认使用control_status
            control_status_key = "control_status"
        
        self._attributes[control_status_key] = control_status

    @property
    def device_name(self):
        return self._device_name

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_type(self):
        return self._device_type

    @property
    def model(self):
        return self._model

    @property
    def sn(self):
        return self._sn

    @property
    def sn8(self):
        return self._sn8

    @property
    def subtype(self):
        return self._subtype

    @property
    def category(self):
        return self._category

    @property
    def attributes(self):
        return self._attributes

    @property
    def connected(self):
        return self._connected

    def set_refresh_interval(self, refresh_interval):
        self._refresh_interval = refresh_interval

    def set_queries(self, queries: list):
        self._queries = queries
        self._skipped_queries.clear()

    def set_cloud_queries(self, cloud_queries: dict):
        self._cloud_queries = cloud_queries or {}

    @staticmethod
    def _query_signature(query) -> tuple:
        if isinstance(query, dict):
            return tuple(sorted(query.items()))
        return (("__raw__", query),)

    def set_centralized(self, centralized: list):
        self._centralized = centralized

    def set_calculate(self, calculate: dict):
        values_get = calculate.get("get")
        values_set = calculate.get("set")
        self._calculate_get = values_get if values_get else []
        self._calculate_set = values_set if values_set else []

    def set_default_values(self, default_values: dict):
        """设置属性的默认值"""
        self._default_values = default_values or {}

    @staticmethod
    def _formula_attribute_names(formula: str) -> list[str]:
        return re.findall(r"\[(\w+)\]", formula)

    def _calculated_get_output_names(self) -> set[str]:
        names: set[str] = set()
        for entry in self._calculate_get:
            lvalue = entry.get("lvalue") or ""
            if lvalue.startswith("[") and lvalue.endswith("]"):
                names.add(lvalue[1:-1])
        return names

    def _calculate_inputs_ready(self, rvalue: str) -> bool:
        attrs = self._formula_attribute_names(rvalue)
        if not attrs:
            return False
        return all(self._attributes.get(attr) is not None for attr in attrs)

    def _calculate_output_name(self, lvalue: str) -> str | None:
        if not (lvalue.startswith("[") and lvalue.endswith("]")):
            return None
        inner = lvalue[1:-1]
        if re.fullmatch(r"\w+", inner):
            return inner
        return None

    def _apply_calculate_get(self, new_status: dict) -> None:
        for c in self._calculate_get:
            lvalue = c.get("lvalue")
            rvalue = c.get("rvalue")
            if not (lvalue and rvalue):
                continue
            if not self._calculate_inputs_ready(rvalue):
                continue
            calculate_str1 = (
                f"{lvalue.replace('[', 'self._attributes[').replace(']', '\"]')} = "
                f"{rvalue.replace('[', 'self._attributes[').replace(']', '\"]')}"
            ).replace("[", "[\"")
            try:
                exec(calculate_str1)
            except Exception:
                traceback.print_exc()
                MideaLogger.warning(
                    f"_apply_calculate_get Calculation Error: {lvalue} = {rvalue}, calculate_str: {calculate_str1}",
                    self._device_id,
                )
                continue

            output_name = self._calculate_output_name(lvalue)
            if output_name is not None and output_name in self._attributes:
                new_status[output_name] = self._attributes[output_name]

    def get_attribute(self, attribute):
        return self._attributes.get(attribute)

    @staticmethod
    def _has_nested_path(attrs: dict, dotted_key: str) -> bool:
        value = attrs
        for key in dotted_key.split("."):
            if not isinstance(value, dict) or key not in value:
                return False
            value = value[key]
        return True

    def _has_attribute(self, attribute: str) -> bool:
        attrs = self._attributes if isinstance(self._attributes, dict) else {}
        if not attrs or attribute in attrs or attribute in LAMP_CONTROL_KEYS:
            return True
        if "." in attribute and attribute.replace(".", "_") in attrs:
            return True
        if "." in attribute and self._has_nested_path(attrs, attribute):
            return True
        return False

    def _get_existing_attr_value(self, attrs: dict, key: str) -> Any:
        if self._has_nested_path(attrs, key):
            val = attrs
            for k in key.split("."):
                val = val[k]
            return val
        if "." in key:
            underscore = key.replace(".", "_")
            if underscore in attrs:
                return attrs[underscore]
        return attrs.get(key)

    def _convert_to_nested_structure(self, attributes):
        """Convert control keys to the device's wire format.

        Dotted mapping keys (e.g. ``mode.current``) become nested objects when
        the device status is nested; otherwise prefer flat underscore / literal
        dotted keys so the same default mapping works for both #216-style and
        Clivet nested 17100001 payloads.
        """
        nested = {}
        attrs = self._attributes if isinstance(self._attributes, dict) else {}
        for key, value in attributes.items():
            existing = self._get_existing_attr_value(attrs, key)
            if isinstance(existing, str) and not isinstance(value, (str, dict, list)):
                value = str(value)

            if "." not in key:
                nested[key] = value
                continue

            underscore = key.replace(".", "_")
            if self._has_nested_path(attrs, key):
                keys = key.split(".")
                current_dict = nested
                for k in keys[:-1]:
                    if k not in current_dict:
                        current_dict[k] = {}
                    current_dict = current_dict[k]
                current_dict[keys[-1]] = value
            elif underscore in attrs:
                nested[underscore] = value
            elif key in attrs:
                nested[key] = value
            else:
                keys = key.split(".")
                current_dict = nested
                for k in keys[:-1]:
                    if k not in current_dict:
                        current_dict[k] = {}
                    current_dict = current_dict[k]
                current_dict[keys[-1]] = value
        return nested

    def _status_for_lua_control(self, control_attributes: dict) -> dict:
        """Exclude lamp states from status when controlling lamps.

        The E3 lua script requires all three lamp_control*_power keys in control,
        and applies status before control. Keeping lamp states in status would
        prevent turning lights off. temperature also maps to cmd[13] and breaks
        the lamp bit field (e.g. 39 -> 0x27 turns all lamps on).
        """
        if not LAMP_CONTROL_KEYS.intersection(control_attributes.keys()):
            return self._attributes

        if set(control_attributes.keys()) <= LAMP_CONTROL_KEYS:
            return {}

        excluded = LAMP_CONTROL_KEYS | LAMP_CONTROL_STATUS_EXCLUDE
        return {
            key: value
            for key, value in self._attributes.items()
            if key not in excluded
        }

    async def set_attribute(self, attribute, value):
        if self._has_attribute(attribute):
            new_status = {}
            for attr in self._centralized:
                new_status[attr] = self._attributes.get(attr)
            new_status[attribute] = value
            
            # 针对T0xD9复式洗衣机，当本地变更 db_location_selection 时，调整 db_location
            if self._device_type == 0xD9:
                if attribute == "db_location_selection":
                    self._handle_t0xd9_db_location_selection(new_status, value)
                # 非 db_location_selection 更新，根据 db_position 设置 db_location
                else:
                    self._adjust_t0xd9_db_location_based_on_position(new_status)

            # Convert dot-notation attributes to nested structure for transmission
            nested_status = self._convert_to_nested_structure(new_status)

            status_for_lua = self._status_for_lua_control(new_status)

            if self._lua_runtime is not None:
                try:
                    if set_cmd := self._lua_runtime.build_control(nested_status, status=status_for_lua):
                        await self._build_send(set_cmd)
                        return
                except Exception as e:
                    MideaLogger.debug(f"LuaRuntimeError in set_attribute {nested_status}: {repr(e)}")
                    traceback.print_exc()

            cloud = self._cloud
            if cloud and hasattr(cloud, "send_device_control"):
                if isinstance(cloud, MSmartHomeCloud):
                    await cloud.send_device_control(
                        appliance_code=self._device_id,
                        device_type=self.device_type,
                        sn=self.sn,
                        model_number=self.subtype,
                        manufacturer_code=self._manufacturer_code,
                        control=nested_status,
                        status=status_for_lua)
                elif isinstance(cloud, MeijuCloud):
                    await cloud.send_device_control(self._device_id, control=nested_status, status=status_for_lua)

    async def set_attributes(self, attributes):
        new_status = {}
        for attr in self._centralized:
            new_status[attr] = self._attributes.get(attr)
        has_new = False
        for attribute, value in attributes.items():
            if self._has_attribute(attribute):
                has_new = True
                new_status[attribute] = value
    
        # 针对T0xD9复式洗衣机，根据 db_location_selection 调整 db_location
        if self._device_type == 0xD9:
            if "db_location_selection" in attributes:
                location_selection = attributes["db_location_selection"]
                self._handle_t0xd9_db_location_selection(new_status, location_selection)
            else:
                # 非 db_location_selection 更新，根据 db_position 设置 db_location
                self._adjust_t0xd9_db_location_based_on_position(new_status)

        # Convert dot-notation attributes to nested structure for transmission
        nested_status = self._convert_to_nested_structure(new_status)
        status_for_lua = self._status_for_lua_control(new_status)
        
        if has_new:
            if self._lua_runtime is not None:
                try:
                    if set_cmd := self._lua_runtime.build_control(nested_status, status=status_for_lua):
                        await self._build_send(set_cmd)
                        return
                except Exception as e:
                    MideaLogger.debug(f"LuaRuntimeError in set_attributes {nested_status}: {repr(e)}")
                    traceback.print_exc()

            cloud = self._cloud
            if cloud and hasattr(cloud, "send_device_control"):
                if isinstance(cloud, MSmartHomeCloud):
                    await cloud.send_device_control(
                        appliance_code=self._device_id,
                        device_type=self.device_type,
                        sn=self.sn,
                        model_number=self.subtype,
                        manufacturer_code=self._manufacturer_code,
                        control=nested_status,
                        status=status_for_lua)
                elif isinstance(cloud, MeijuCloud):
                    await cloud.send_device_control(self._device_id, control=nested_status, status=status_for_lua)

    def set_ip_address(self, ip_address):
        MideaLogger.debug(f"Update IP address to {ip_address}")
        self._ip_address = ip_address
        self.close_socket()

    def send_command(self, cmd_type, cmd_body: bytearray):
        cmd = MessageQuestCustom(self._device_type, cmd_type, cmd_body)
        try:
            self._build_send(cmd.serialize().hex())
        except socket.error as e:
            MideaLogger.debug(
                f"Interface send_command failure, {repr(e)}, "
                f"cmd_type: {cmd_type}, cmd_body: {cmd_body.hex()}",
                self._device_id
            )

    def register_update(self, update):
        self._updates.append(update)

    @staticmethod
    def _fetch_v2_message(msg):
        result = []
        while len(msg) > 0:
            factual_msg_len = len(msg)
            if factual_msg_len < 6:
                break
            alleged_msg_len = msg[4] + (msg[5] << 8)
            if factual_msg_len >= alleged_msg_len:
                result.append(msg[:alleged_msg_len])
                msg = msg[alleged_msg_len:]
            else:
                break
        return result, msg

    def _authenticate(self):
        request = self._security.encode_8370(
            self._token, MSGTYPE_HANDSHAKE_REQUEST)
        MideaLogger.debug(f"Handshaking")
        self._socket.send(request)
        response = self._socket.recv(512)
        if len(response) < 20:
            raise AuthException()
        response = response[8: 72]
        self._security.tcp_key(response, self._key)

    def _send_message_v2(self, data):
        if self._socket is not None:
            self._socket.send(data)
        else:
            MideaLogger.debug(f"Command send failure, device disconnected, data: {data.hex()}")

    def _send_message_v3(self, data, msg_type=MSGTYPE_ENCRYPTED_REQUEST):
        data = self._security.encode_8370(data, msg_type)
        self._send_message_v2(data)

    async def _build_send(self, cmd: str):
        MideaLogger.debug(f"Sending: {cmd.lower()}")
        bytes_cmd = bytes.fromhex(cmd)
        await self._send_message(bytes_cmd)

    async def refresh_status(self):
        for query in self._queries:
            query_sig = self._query_signature(query)
            if query_sig in self._skipped_queries:
                continue

            # 针对T0xD9复式洗衣机，根据 db_position 动态调整 db_location
            actual_query = query.copy() if isinstance(query, dict) else query
            if self._device_type == 0xD9 and isinstance(actual_query, dict):
                # 根据 db_position 调整 db_location
                calculated_location = self._adjust_t0xd9_db_location_based_on_position(actual_query)

                # 同步更新db_location_selection
                self._sync_t0xd9_location_selection(calculated_location)

            cloud = self._cloud
            if cloud and hasattr(cloud, "get_device_status"):
                if isinstance(cloud, MSmartHomeCloud):
                    if status := await cloud.get_device_status(
                        appliance_code=self._device_id,
                        device_type=self.device_type,
                        sn=self.sn,
                        model_number=self.subtype,
                        manufacturer_code=self._manufacturer_code,
                        query=actual_query
                    ):
                        self._parse_cloud_message(status)
                    elif cloud.lua_status_analysis_error:
                        self._skipped_queries.add(query_sig)
                        MideaLogger.warning(
                            f"Cloud lua analysis exception for query {query}, "
                            f"skip further retries. msg={cloud.lua_status_analysis_msg}"
                        )
                    else:
                        if self._lua_runtime is not None:
                            if query_cmd := self._lua_runtime.build_query(actual_query):
                                await self._build_send(query_cmd)

                elif isinstance(cloud, MeijuCloud):
                    if status := await cloud.get_device_status(
                        appliance_code=self._device_id,
                        query=actual_query
                    ):
                        self._parse_cloud_message(status)
                    elif cloud.lua_status_analysis_error:
                        self._skipped_queries.add(query_sig)
                        MideaLogger.warning(
                            f"Cloud lua analysis exception for query {query}, "
                            f"skip further retries. msg={cloud.lua_status_analysis_msg}"
                        )
                    else:
                        if self._lua_runtime is not None:
                            if query_cmd := self._lua_runtime.build_query(actual_query):
                                await self._build_send(query_cmd)


    def _parse_cloud_message(self, status, update=True):
        # MideaLogger.debug(f"Received: {decrypted}")
        new_status = {}
        calculated_outputs = self._calculated_get_output_names()
        # 对于有默认值的变量，在解析前先设置一次默认值
        for attr, default_value in self._default_values.items():
            # self._attributes[attr] = default_value
            if attr not in self._attributes or self._attributes[attr] is None:
                new_status[attr] = default_value

        # 处理云端返回的状态，云端结果会覆盖默认值
        for single in status.keys():
            value = status.get(single)
            if value is None and single in calculated_outputs:
                continue
            if single not in self._attributes or self._attributes[single] != value:
                # self._attributes[single] = value
                new_status[single] = value

        # 对于T0xD9复式洗衣机，依据云端 db_running_status，调整本地 db_control_status
        if self._device_type == 0xD9 and "db_running_status" in new_status:
            running_status = new_status["db_running_status"]
            self._adjust_control_status(running_status)

        # 对于T0xDA、T0xDB、T0xDC设备，依据云端 running_status，调整本地 control_status
        if self._device_type in [0xDA, 0xDB, 0xDC] and "running_status" in new_status:
            running_status = new_status["running_status"]
            self._adjust_control_status(running_status)

        if new_status:
            for key, value in new_status.items():
                self._attributes[key] = value

        if status:
            self._apply_calculate_get(new_status)
            if self._cloud is not None and self._ip_address is None:
                self._device_connected(True)

        if update and new_status:
            self._update_all(new_status)
        return ParseMessageResult.SUCCESS

    def _parse_message(self, msg, update=True):
        if self._protocol == 3:
            messages, self._buffer = self._security.decode_8370(self._buffer + msg)
        else:
            messages, self._buffer = self.fetch_v2_message(self._buffer + msg)
        if len(messages) == 0:
            return ParseMessageResult.PADDING
        for message in messages:
            if message == b"ERROR":
                return ParseMessageResult.ERROR
            payload_len = message[4] + (message[5] << 8) - 56
            payload_type = message[2] + (message[3] << 8)
            if payload_type in [0x1001, 0x0001]:
                # Heartbeat detected
                pass
            elif len(message) > 56:
                cryptographic = message[40:-16]
                if payload_len % 16 == 0:
                    decrypted = self._security.aes_decrypt(cryptographic)
                    MideaLogger.debug(f"Received: {decrypted.hex().lower()}")
                    if status := self._lua_runtime.decode_status(decrypted.hex()):
                        MideaLogger.debug(f"Decoded: {status}")
                        new_status = {}
                        calculated_outputs = self._calculated_get_output_names()
                        for single in status.keys():
                            value = status.get(single)
                            if value is None and single in calculated_outputs:
                                continue
                            if single not in self._attributes or self._attributes[single] != value:
                                new_status[single] = value
                        if new_status:
                            for key, value in new_status.items():
                                self._attributes[key] = value
                        self._apply_calculate_get(new_status)
                        if update and new_status:
                            self._update_all(new_status)
        return ParseMessageResult.SUCCESS

    async def _send_message(self, data):
        if reply := await self._cloud.send_cloud(self._device_id, data):
            if reply_dec := self._lua_runtime.decode_status(dec_string_to_bytes(reply).hex()):
                MideaLogger.debug(f"Decoded: {reply_dec}")
                result = self._parse_cloud_message(reply_dec, update=False)
                if result == ParseMessageResult.ERROR:
                    MideaLogger.debug(f"Message 'ERROR' received")
                elif result == ParseMessageResult.SUCCESS:
                    timeout_counter = 0

    # if self._protocol == 3:
    #     self._send_message_v3(data, msg_type=MSGTYPE_ENCRYPTED_REQUEST)
    # else:
    #     self._send_message_v2(data)

    async def _send_heartbeat(self):
        msg = PacketBuilder(self._device_id, bytearray([0x00])).finalize(msg_type=0)
        await self._send_message(msg)

    def _device_connected(self, connected=True):
        self._connected = connected
        status = {"connected": connected}
        if not connected:
            MideaLogger.warning(f"Device {self._device_id} disconnected", self._device_id)
        else:
            MideaLogger.debug(f"Device {self._device_id} connected", self._device_id)
        self._update_all(status)

    def _update_all(self, status):
        MideaLogger.debug(f"Status update: {status}")
        for update in self._updates:
            update(status)

    # def open(self):
    #     if not self._is_run:
    #         self._is_run = True
    #         threading.Thread.start(self)
    #
    # def close(self):
    #     if self._is_run:
    #         self._is_run = False
    #         self._lua_runtime = None
    #         self.disconnect()
    #
    # def run(self):
    #     while self._is_run:
    #         while self._socket is None:
    #             if self.connect(refresh=True) is False:
    #                 if not self._is_run:
    #                     return
    #                 self.disconnect()
    #                 time.sleep(5)
    #         timeout_counter = 0
    #         start = time.time()
    #         previous_refresh = start
    #         previous_heartbeat = start
    #         self._socket.settimeout(1)
    #         while True:
    #             try:
    #                 now = time.time()
    #                 if 0 < self._refresh_interval <= now - previous_refresh:
    #                     self._refresh_status()
    #                     previous_refresh = now
    #                 if now - previous_heartbeat >= self._heartbeat_interval:
    #                     self._send_heartbeat()
    #                     previous_heartbeat = now
    #                 msg = self._socket.recv(512)
    #                 msg_len = len(msg)
    #                 if msg_len == 0:
    #                     raise socket.error("Connection closed by peer")
    #                 result = self._parse_message(msg)
    #                 if result == ParseMessageResult.ERROR:
    #                     MideaLogger.debug(f"Message 'ERROR' received")
    #                     self.disconnect()
    #                     break
    #                 elif result == ParseMessageResult.SUCCESS:
    #                     timeout_counter = 0
    #             except socket.timeout:
    #                 timeout_counter = timeout_counter + 1
    #                 if timeout_counter >= 120:
    #                     MideaLogger.debug(f"Heartbeat timed out")
    #                     self.disconnect()
    #                     break
    #             except socket.error as e:
    #                 MideaLogger.debug(f"Socket error {repr(e)}")
    #                 self.disconnect()
    #                 break
    #             except Exception as e:
    #                 MideaLogger.error(f"Unknown error :{e.__traceback__.tb_frame.f_globals['__file__']}, "
    #                                   f"{e.__traceback__.tb_lineno}, {repr(e)}")
    #                 self.disconnect()
    #                 break
