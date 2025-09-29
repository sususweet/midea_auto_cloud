import threading
import socket
from enum import IntEnum

from .cloud import MideaCloud
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
        self._attributes = {
            "device_type": "T0x%02X" % device_type,
            "sn": sn,
            "sn8": sn8,
            "subtype": subtype
        }
        self._refresh_interval = 30
        self._heartbeat_interval = 10
        self._device_connected(connected)
        self._queries = [{}]
        self._centralized = []
        self._calculate_get = []
        self._calculate_set = []
        self._lua_runtime = MideaCodec(lua_file, sn=sn, subtype=subtype) if lua_file is not None else None
        self._cloud = cloud

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
    def attributes(self):
        return self._attributes

    @property
    def connected(self):
        return self._connected

    def set_refresh_interval(self, refresh_interval):
        self._refresh_interval = refresh_interval

    def set_queries(self, queries: list):
        self._queries = queries

    def set_centralized(self, centralized: list):
        self._centralized = centralized

    def set_calculate(self, calculate: dict):
        values_get = calculate.get("get")
        values_set = calculate.get("set")
        self._calculate_get = values_get if values_get else []
        self._calculate_set = values_set if values_set else []

    def get_attribute(self, attribute):
        return self._attributes.get(attribute)

    async def set_attribute(self, attribute, value):
        if attribute in self._attributes.keys():
            new_status = {}
            for attr in self._centralized:
                new_status[attr] = self._attributes.get(attr)
            new_status[attribute] = value
            try:
                if set_cmd := self._lua_runtime.build_control(new_status):
                    await self._build_send(set_cmd)
            except Exception as e:
                cloud = self._cloud
                if cloud and hasattr(cloud, "send_device_control"):
                    await cloud.send_device_control(self._device_id, control=new_status, status=self._attributes)

    async def set_attributes(self, attributes):
        new_status = {}
        for attr in self._centralized:
            new_status[attr] = self._attributes.get(attr)
        has_new = False
        for attribute, value in attributes.items():
            if attribute in self._attributes.keys():
                has_new = True
                new_status[attribute] = value
        if has_new:
            try:
                if set_cmd := self._lua_runtime.build_control(new_status):
                    await self._build_send(set_cmd)
            except Exception as e:
                cloud = self._cloud
                if cloud and hasattr(cloud, "send_device_control"):
                    await cloud.send_device_control(self._device_id, control=new_status, status=self._attributes)

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
            if query_cmd := self._lua_runtime.build_query(query):
                await self._build_send(query_cmd)

    def _parse_cloud_message(self, decrypted):
        # MideaLogger.debug(f"Received: {decrypted}")
        if status := self._lua_runtime.decode_status(dec_string_to_bytes(decrypted).hex()):
            MideaLogger.debug(f"Decoded: {status}")
            new_status = {}
            for single in status.keys():
                value = status.get(single)
                if single not in self._attributes or self._attributes[single] != value:
                    self._attributes[single] = value
                    new_status[single] = value
            if len(new_status) > 0:
                for c in self._calculate_get:
                    lvalue = c.get("lvalue")
                    rvalue = c.get("rvalue")
                    if lvalue and rvalue:
                        calculate = False
                        for s, v in new_status.items():
                            if rvalue.find(f"[{s}]") >= 0:
                                calculate = True
                                break
                        if calculate:
                            calculate_str1 = \
                                (f"{lvalue.replace('[', 'self._attributes[')} = "
                                 f"{rvalue.replace('[', 'self._attributes[')}") \
                                    .replace("[", "[\"").replace("]", "\"]")
                            calculate_str2 = \
                                (f"{lvalue.replace('[', 'new_status[')} = "
                                 f"{rvalue.replace('[', 'self._attributes[')}") \
                                    .replace("[", "[\"").replace("]", "\"]")
                            try:
                                exec(calculate_str1)
                                exec(calculate_str2)
                            except Exception:
                                MideaLogger.warning(
                                    f"Calculation Error: {lvalue} = {rvalue}", self._device_id
                                )
                self._update_all(new_status)
        return ParseMessageResult.SUCCESS

    def _parse_message(self, msg):
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
                        for single in status.keys():
                            value = status.get(single)
                            if single not in self._attributes or self._attributes[single] != value:
                                self._attributes[single] = value
                                new_status[single] = value
                        if len(new_status) > 0:
                            for c in self._calculate_get:
                                lvalue = c.get("lvalue")
                                rvalue = c.get("rvalue")
                                if lvalue and rvalue:
                                    calculate = False
                                    for s, v in new_status.items():
                                        if rvalue.find(f"[{s}]") >= 0:
                                            calculate = True
                                            break
                                    if calculate:
                                        calculate_str1 = \
                                            (f"{lvalue.replace('[', 'self._attributes[')} = "
                                             f"{rvalue.replace('[', 'self._attributes[')}") \
                                                .replace("[", "[\"").replace("]", "\"]")
                                        calculate_str2 = \
                                            (f"{lvalue.replace('[', 'new_status[')} = "
                                             f"{rvalue.replace('[', 'self._attributes[')}") \
                                                .replace("[", "[\"").replace("]", "\"]")
                                        try:
                                            exec(calculate_str1)
                                            exec(calculate_str2)
                                        except Exception:
                                            MideaLogger.warning(
                                                f"Calculation Error: {lvalue} = {rvalue}", self._device_id
                                            )
                            self._update_all(new_status)
        return ParseMessageResult.SUCCESS

    async def _send_message(self, data):
        if reply := await self._cloud.send_cloud(self._device_id, data):
            result = self._parse_cloud_message(reply)
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


