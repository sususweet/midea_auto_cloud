import logging
import time
import datetime
import json
import base64
import traceback
import os
import aiofiles
import requests
from aiohttp import ClientSession
from secrets import token_hex
from .logger import MideaLogger
from .security import CloudSecurity, MeijuCloudSecurity, MSmartCloudSecurity
from .util import bytes_to_dec_string

_LOGGER = logging.getLogger(__name__)

clouds = {
    "美的美居": {
        "class_name": "MeijuCloud",
        "app_key": "46579c15",
        "login_key": "ad0ee21d48a64bf49f4fb583ab76e799",
        "iot_key": bytes.fromhex(format(9795516279659324117647275084689641883661667, 'x')).decode(),
        "hmac_key": bytes.fromhex(format(117390035944627627450677220413733956185864939010425, 'x')).decode(),
        "api_url": "https://mp-prod.smartmidea.net/mas/v5/app/proxy?alias=",
    },
    "MSmartHome": {
        "class_name": "MSmartHomeCloud",
        "app_key": "ac21b9f9cbfe4ca5a88562ef25e2b768",
        "iot_key": bytes.fromhex(format(7882822598523843940, 'x')).decode(),
        "hmac_key": bytes.fromhex(format(117390035944627627450677220413733956185864939010425, 'x')).decode(),
        "api_url": "https://mp-prod.appsmb.com/mas/v5/app/proxy?alias=",
    },
}

default_keys = {
    99: {
        "token": "ee755a84a115703768bcc7c6c13d3d629aa416f1e2fd798beb9f78cbb1381d09"
                 "1cc245d7b063aad2a900e5b498fbd936c811f5d504b2e656d4f33b3bbc6d1da3",
        "key": "ed37bd31558a4b039aaf4e7a7a59aa7a75fd9101682045f69baf45d28380ae5c"
    }
}


class MideaCloud:
    def __init__(
            self,
            session: ClientSession,
            security: CloudSecurity,
            app_key: str,
            account: str,
            password: str,
            api_url: str,
            proxy: str | None = None
    ):
        self._device_id = CloudSecurity.get_deviceid(account)
        self._session = session
        self._security = security
        self._app_key = app_key
        self._account = account
        self._password = password
        self._api_url = api_url
        self._proxy = proxy
        self._access_token = None
        self._login_id = None

    def _make_general_data(self):
        return {}

    async def _api_request(self, endpoint: str, data: dict, header=None, method="POST") -> dict | None:
        header = header or {}
        if not data.get("reqId"):
            data.update({
                "reqId": token_hex(16)
            })
        if not data.get("stamp"):
            data.update({
                "stamp":  datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            })
        random = str(int(time.time()))
        url = self._api_url + endpoint
        dump_data = json.dumps(data)
        sign = self._security.sign(dump_data, random)
        header.update({
            "content-type": "application/json; charset=utf-8",
            "secretVersion": "1",
            "sign": sign,
            "random": random,
        })
        if self._access_token is not None:
            header.update({
                "accesstoken": self._access_token
            })
        response:dict = {"code": -1}
        _LOGGER.debug(f"Midea cloud API url: {url}, header: {header}, data: {data}")
        try:
            r = await self._session.request(
                method, 
                url, 
                headers=header, 
                data=dump_data, 
                timeout=30,
                proxy=self._proxy
            )
            raw = await r.read()
            _LOGGER.debug(f"Midea cloud API url: {url}, header: {header}, data: {data}, response: {raw}")
            response = json.loads(raw)
        except Exception as e:
            traceback.print_exc()

        if int(response["code"]) == 0:
            if "data" in response:
                return response["data"]
            else:
                return {"message": "ok"}

        return None

    def _api_request_sync(self, endpoint: str, data: dict, header=None) -> dict | None:
        header = header or {}
        if not data.get("reqId"):
            data.update({
                "reqId": token_hex(16)
            })
        if not data.get("stamp"):
            data.update({
                "stamp":  datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            })
        random = str(int(time.time()))
        url = self._api_url + endpoint
        dump_data = json.dumps(data)
        sign = self._security.sign(dump_data, random)
        header.update({
            "content-type": "application/json; charset=utf-8",
            "secretVersion": "1",
            "sign": sign,
            "random": random,
        })
        if self._access_token is not None:
            header.update({
                "accesstoken": self._access_token
            })
        response:dict = {"code": -1}
        _LOGGER.debug(f"Midea cloud API header: {header}")
        _LOGGER.debug(f"Midea cloud API dump_data: {dump_data}")
        try:
            r = requests.post(url, headers=header, data=dump_data, timeout=5)
            raw = r.content
            _LOGGER.debug(f"Midea cloud API url: {url}, data: {data}, response: {raw}")
            response = json.loads(raw)
        except Exception as e:
            traceback.print_exc()

        if int(response["code"]) == 0 and "data" in response:
            return response["data"]

        return None

    async def _get_login_id(self) -> str | None:
        data = self._make_general_data()
        data.update({
            "loginAccount": f"{self._account}",
            "type": "1",
        })
        if response := await self._api_request(
            endpoint="/v1/user/login/id/get",
            data=data
        ):
            return response.get("loginId")
        return None

    async def login(self) -> bool:
        raise NotImplementedError()

    async def list_home(self) -> dict | None:
        return {1: "My home"}

    async def list_appliances(self, home_id) -> dict | None:
        raise NotImplementedError()

    async def download_lua(
            self, path: str,
            device_type: int,
            sn: str,
            model_number: str | None,
            manufacturer_code: str = "0000",
    ):
        raise NotImplementedError()

    async def download_plugin(
            self, path: str,
            appliance_code: str,
            smart_product_id: str,
            device_type: int,
            sn: str,
            sn8: str,
            model_number: str | None,
            manufacturer_code: str = "0000",
    ):
        raise NotImplementedError()

    async def send_central_ac_control(self, appliance_code: int, nodeid: str, modelid: str, idtype: int, control: dict) -> bool:
        """Send control to central AC subdevice. Subclasses should implement if supported."""
        raise NotImplementedError()
    
    async def get_central_ac_status(self, appliance_codes: list) -> dict | None:
        """Get status of central AC devices. Subclasses should implement if supported."""
        raise NotImplementedError()

    async def send_switch_control(self, device_id: str, nodeid: str, switch_control: dict) -> bool:
        """Send control to switch device. Subclasses should implement if supported."""
        raise NotImplementedError()


class MeijuCloud(MideaCloud):
    APP_ID = "900"
    APP_VERSION = "8.20.0.2"

    def __init__(
            self,
            cloud_name: str,
            session: ClientSession,
            account: str,
            password: str,
            proxy: str | None = None,
    ):
        super().__init__(
            session=session,
            security=MeijuCloudSecurity(
                login_key=clouds[cloud_name]["login_key"],
                iot_key=clouds[cloud_name]["iot_key"],
                hmac_key=clouds[cloud_name]["hmac_key"],
            ),
            app_key=clouds[cloud_name]["app_key"],
            account=account,
            password=password,
            api_url=clouds[cloud_name]["api_url"],
            proxy=proxy
        )
        self._homegroup_id = None

    async def login(self) -> bool:
        if login_id := await self._get_login_id():
            self._login_id = login_id
            stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            data = {
                "iotData": {
                    "clientType": 1,
                    "deviceId": self._device_id,
                    "iampwd": self._security.encrypt_iam_password(self._login_id, self._password),
                    "iotAppId": self.APP_ID,
                    "loginAccount": self._account,
                    "password": self._security.encrypt_password(self._login_id, self._password),
                    "reqId": token_hex(16),
                    "stamp": stamp
                },
                "data": {
                    "appKey": self._app_key,
                    "deviceId": self._device_id,
                    "platform": 2
                },
                "timestamp": stamp,
                "stamp": stamp
            }
            if response := await self._api_request(
                endpoint="/mj/user/login",
                data=data
            ):
                self._access_token = response["mdata"]["accessToken"]
                self._security.set_aes_keys(
                    self._security.aes_decrypt_with_fixed_key(
                        response["key"]
                    ), None
                )

                return True
        return False

    async def list_home(self):
        if response := await self._api_request(
            endpoint="/v1/homegroup/list/get",
            data={}
        ):
            homes = {}
            for home in response["homeList"]:
                homes.update({
                    int(home["homegroupId"]): home["name"]
                })
            return homes
        return None

    async def list_appliances(self, home_id) -> dict | None:
        # 存储当前使用的 homegroupId 用于后续的中央空调控制
        self._homegroup_id = str(home_id)
        data = {
            "homegroupId": home_id
        }
        if response := await self._api_request(
            endpoint="/v1/appliance/home/list/get",
            data=data
        ):
            appliances = {}
            for home in response.get("homeList") or []:
                for room in home.get("roomList") or []:
                    for appliance in room.get("applianceList"):
                        device_info = {
                            "name": appliance.get("name"),
                            "type": int(appliance.get("type"), 16),
                            "sn": self._security.aes_decrypt(appliance.get("sn")) if appliance.get("sn") else "",
                            "sn8": appliance.get("sn8", "00000000"),
                            "smart_product_id": appliance.get("smartProductId", "0"),
                            "model_number": appliance.get("modelNumber", "0"),
                            "manufacturer_code": appliance.get("enterpriseCode", "0000"),
                            "model": appliance.get("productModel"),
                            "online": appliance.get("onlineStatus") == "1",
                        }
                        if device_info.get("sn8") is None or len(device_info.get("sn8")) == 0:
                            device_info["sn8"] = "00000000"
                        if device_info.get("model") is None or len(device_info.get("model")) == 0:
                            device_info["model"] = device_info["sn8"]
                        appliances[int(appliance["applianceCode"])] = device_info
            return appliances
        return None

    async def send_cloud(self, appliance_id: int, data: bytearray):
        appliance_code = str(appliance_id)
        params = {
            'applianceCode': appliance_code,
            'order': self._security.aes_encrypt(bytes_to_dec_string(data)).hex(),
            'timestamp': 'true',
            "isFull": "false"
        }

        if response := await self._api_request(
            endpoint='/v1/appliance/transparent/send',
            data=params,
        ):
            if response and response.get('reply'):
                _LOGGER.debug("[%s] Cloud command response: %s", appliance_code, response)
                reply_data = self._security.aes_decrypt(bytes.fromhex(response['reply']))
                return reply_data
            else:
                _LOGGER.warning("[%s] Cloud command failed: %s", appliance_code, response)

        return None

    async def get_device_status(self, appliance_code: int, query: dict) -> dict | None:
        data = {
            "applianceCode": str(appliance_code),
            "command": {
                "query": query
            }
        }
        if response := await self._api_request(
            endpoint="/mjl/v1/device/status/lua/get",
            data=data
        ):
            # 预期返回形如 { ... 状态键 ... }
            return response
        return None

    async def send_device_control(self, appliance_code: int, control: dict, status: dict | None = None) -> bool:
        data = {
            "applianceCode": str(appliance_code),
            "command": {
                "control": control
            }
        }
        if status and isinstance(status, dict):
            data["command"]["status"] = status
        response = await self._api_request(
            endpoint="/mjl/v1/device/lua/control",
            data=data
        )
        return response is not None
    
    async def send_central_ac_control(self, appliance_code: int, nodeid: str, modelid: str, idtype: int, control: dict) -> bool:
        """Send control to central AC subdevice using the special T0x21 API."""
        import uuid
        import json
        
        # 构建中央空调控制命令
        command_data = {
            "nodeid": nodeid,
            "acattri_ctrl": {
                "nodeid": nodeid,
                "modelid": modelid, "type": idtype, "aclist_data": nodeid[-2:],
                "event": control
            }
        }
        
        # 构建完整的请求数据
        request_data = {
            "applianceCode": str(appliance_code),
            "modelId": modelid,
            "topic": "/subdevice/multicontrol",
            "command": command_data,
            "msgId": str(uuid.uuid4()).replace("-", "")
        }
        request_data_str = json.dumps(request_data).encode("utf-8")
        MideaLogger.debug(f"Sending control to central AC device {appliance_code}: {request_data_str}")
        # 发送到特殊的中央空调API
        if response := await self._api_request(
            endpoint="/v1/gateway/transport/send",
            data={
                'applianceCode': str(appliance_code),
                'order': self._security.aes_encrypt(request_data_str).hex(),
                'homegroupId': self._homegroup_id,
            }
        ):
            if response and response.get('reply'):
                reply_data = self._security.aes_decrypt(bytes.fromhex(response['reply']))
                MideaLogger.debug(f"[{appliance_code}] Gateway command response: {reply_data}")
                return reply_data
            else:
                MideaLogger.warning(f"[{appliance_code}] Gateway command failed: {response}")


    async def get_central_ac_status(self, appliance_codes: list) -> dict | None:
        """Get status of central AC devices using the aggregator API."""

        # 构建请求数据
        request_data = {
            "entities": ["endlist", "tips"],
            "appliances": [{"id": str(code), "type": "0x21"} for code in appliance_codes],
        }
        
        response = await self._api_request(
            endpoint="/api/v1/aggregator/appliances",
            data=request_data
        )
        return response

    async def send_switch_control(self, device_id: str, nodeid: str, switch_control: dict) -> bool:
        """Send control to switch device using the controlPanelFour API with PUT method."""
        import uuid
        
        # switch_control 格式: {"endPoint": 1, "attribute": 0}
        end_point = switch_control.get("endPoint", 1)
        attribute = switch_control.get("attribute", 0)
        
        # 构建请求数据
        request_data = {
            "msgId": str(uuid.uuid4()).replace("-", ""),
            "deviceControlList": [{
                "endPoint": end_point,
                "attribute": attribute
            }],
            "deviceId": device_id,
            "nodeId": nodeid
        }
        
        MideaLogger.debug(f"Sending switch control to device {device_id}: {request_data}")
        
        # 使用PUT方法发送到开关控制API
        if response := await self._api_request(
            endpoint="/v1/appliance/operation/controlPanelFour/" + device_id,
            data=request_data,
            method="PUT"
        ):
            MideaLogger.debug(f"[{device_id}] Switch control response: {response}")
            return True
        else:
            MideaLogger.warning(f"[{device_id}] Switch control failed: {response}")
            return False

    async def download_lua(
            self, path: str,
            device_type: int,
            sn: str,
            model_number: str | None,
            manufacturer_code: str = "0000",
    ):
        data = {
            "applianceSn": sn,
            "applianceType": "0x%02X" % device_type,
            "applianceMFCode": manufacturer_code,
            'version': "0",
            "iotAppId": self.APP_ID,
            "modelNumber": model_number
        }
        fnm = None
        if response := await self._api_request(
            endpoint="/v1/appliance/protocol/lua/luaGet",
            data=data
        ):
            res = await self._session.get(response["url"])
            if res.status == 200:
                lua = await res.text()
                if lua:
                    stream = ('local bit = require "bit"\n' +
                              self._security.aes_decrypt_with_fixed_key(lua))
                    stream = stream.replace("\r\n", "\n")
                    fnm = f"{path}/{response['fileName']}"
                    async with aiofiles.open(fnm, "w") as fp:
                        await fp.write(stream)
        return fnm


    async def download_plugin(
            self, path: str,
            appliance_code: str,
            smart_product_id: str,
            device_type: int,
            sn: str,
            sn8: str,
            model_number: str | None,
            manufacturer_code: str = "0000",
    ):
        # 构建 applianceList，根据传入的参数动态生成
        appliance_info = {
            "appModel": sn8,
            "appEnterprise": manufacturer_code,
            "appType": f"0x{device_type:02X}",
            "applianceCode": str(appliance_code) if isinstance(appliance_code, int) else appliance_code,
            "smartProductId": str(smart_product_id) if isinstance(smart_product_id, int) else smart_product_id,
            "modelNumber": model_number or "0",
            "versionCode": 0
        }
        appliance_list = [appliance_info]
        data = {
            "applianceList": json.dumps(appliance_list),
            "iotAppId": self.APP_ID,
            "match": "1",
            "clientType": "1",
            "clientVersion": 201
        }
        fnm = None
        if response := await self._api_request(
            endpoint="/v1/plugin/update/getPluginV3",
            data=data
        ):
            # response 是 {"list": [...]}
            plugin_list = response.get("list", [])
            if not plugin_list:
                MideaLogger.warning(f"No plugin found for device type 0x{device_type:02X}, sn: {sn}")
                return None
            
            # 找到匹配的设备（优先匹配 applianceCode，其次匹配 appType）
            matched_plugin = None
            # 首先尝试精确匹配 applianceCode
            for plugin in plugin_list:
                if plugin.get("applianceCode") == sn and plugin.get("appType") == f"0x{device_type:02X}":
                    matched_plugin = plugin
                    break
            
            # 如果没有精确匹配，使用第一个匹配 appType 的
            if not matched_plugin:
                for plugin in plugin_list:
                    if plugin.get("appType") == f"0x{device_type:02X}":
                        matched_plugin = plugin
                        break
            
            if not matched_plugin:
                MideaLogger.warning(f"No matching plugin found for device type 0x{device_type:02X}, sn: {sn}")
                return None
            
            # 下载 zip 文件
            zip_url = matched_plugin.get("url")
            zip_title = matched_plugin.get("title", f"plugin_0x{device_type:02X}.zip")
            
            if not zip_url:
                MideaLogger.warning(f"No download URL found for plugin: {zip_title}")
                return None
            
            try:
                # 确保目录存在
                os.makedirs(path, exist_ok=True)
                
                res = await self._session.get(zip_url)
                if res.status == 200:
                    zip_data = await res.read()
                    if zip_data:
                        fnm = f"{path}/{zip_title}"
                        async with aiofiles.open(fnm, "wb") as fp:
                            await fp.write(zip_data)
                        MideaLogger.info(f"Downloaded plugin file: {fnm}")
                    else:
                        MideaLogger.warning(f"Downloaded zip file is empty: {zip_url}")
                else:
                    MideaLogger.warning(f"Failed to download plugin, status: {res.status}, url: {zip_url}")
            except Exception as e:
                MideaLogger.error(f"Error downloading plugin: {e}")
                traceback.print_exc()
        return fnm

class MSmartHomeCloud(MideaCloud):
    APP_ID = "1010"
    SRC = "10"
    APP_VERSION = "3.0.2"

    def __init__(
            self,
            cloud_name: str,
            session: ClientSession,
            account: str,
            password: str,
            proxy: str | None = None,
    ):
        super().__init__(
            session=session,
            security=MSmartCloudSecurity(
                login_key=clouds[cloud_name]["app_key"],
                iot_key=clouds[cloud_name]["iot_key"],
                hmac_key=clouds[cloud_name]["hmac_key"],
            ),
            app_key=clouds[cloud_name]["app_key"],
            account=account,
            password=password,
            api_url=clouds[cloud_name]["api_url"],
            proxy=proxy
        )
        self._auth_base = base64.b64encode(
            f"{self._app_key}:{clouds['MSmartHome']['iot_key']}".encode("ascii")
        ).decode("ascii")
        self._uid = ""

    def _make_general_data(self):
        return {
            "appVersion": self.APP_VERSION,
            "src": self.SRC,
            "format": "2",
            "stamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "platformId": "1",
            "deviceId": self._device_id,
            "reqId": token_hex(16),
            "uid": self._uid,
            "clientType": "1",
            "appId": self.APP_ID,
        }

    async def _api_request(self, endpoint: str, data: dict, header=None) -> dict | None:
        header = header or {}
        header.update({
            "x-recipe-app": self.APP_ID,
            "authorization": f"Basic {self._auth_base}"
        })
        if len(self._uid) > 0:
            header.update({
                "uid": self._uid
            })
        return await super()._api_request(endpoint, data, header)

    async def _re_route(self):
        data = self._make_general_data()
        data.update({
            "userName": f"{self._account}",
            "platformId": "1",
            "userType": "0"
        })
        if response := await self._api_request(
            endpoint="/v1/unitcenter/router/user/name",
            data=data
        ):
            if api_url := response.get("masUrl"):
                self._api_url = api_url

    async def login(self) -> bool:
        await self._re_route()
        if login_id := await self._get_login_id():
            self._login_id = login_id
            iot_data = self._make_general_data()
            iot_data.pop("uid")
            stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            iot_data.update({
                "iampwd": self._security.encrypt_iam_password(self._login_id, self._password),
                "loginAccount": self._account,
                "password": self._security.encrypt_password(self._login_id, self._password),
                "stamp": stamp
            })
            data = {
                "iotData": iot_data,
                "data": {
                    "appKey": self._app_key,
                    "deviceId": self._device_id,
                    "platform": "2"
                },
                "stamp": stamp
            }
            if response := await self._api_request(
                endpoint="/mj/user/login",
                data=data
            ):
                self._uid = response["uid"]
                self._access_token = response["mdata"]["accessToken"]
                self._security.set_aes_keys(response["accessToken"], response["randomData"])
                return True
        return False

    async def list_appliances(self, home_id=None) -> dict | None:
        data = self._make_general_data()
        if response := await self._api_request(
            endpoint="/v1/appliance/user/list/get",
            data=data
        ):
            appliances = {}
            for appliance in response["list"]:
                device_info = {
                    "name": appliance.get("name"),
                    "type": int(appliance.get("type"), 16),
                    "sn": self._security.aes_decrypt(appliance.get("sn")) if appliance.get("sn") else "",
                    "sn8": "",
                    "model_number": appliance.get("modelNumber", "0"),
                    "manufacturer_code":appliance.get("enterpriseCode", "0000"),
                    "model": "",
                    "online": appliance.get("onlineStatus") == "1",
                }
                device_info["sn8"] = device_info.get("sn")[9:17] if len(device_info["sn"]) > 17 else ""
                device_info["model"] = device_info.get("sn8")
                appliances[int(appliance["id"])] = device_info
            return appliances
        return None

    async def download_lua(
        self, path: str,
        device_type: int,
        sn: str,
        model_number: str | None,
        manufacturer_code: str = "0000",
    ):
        data = {
            "clientType": "1",
            "appId": self.APP_ID,
            "format": "2",
            "deviceId": self._device_id,
            "iotAppId": self.APP_ID,
            "applianceMFCode": manufacturer_code,
            "applianceType": "0x%02X" % device_type,
            "modelNumber": model_number,
            "applianceSn": self._security.aes_encrypt_with_fixed_key(sn.encode("ascii")).hex(),
            "version": "0",
            "encryptedType ": "2"
        }
        fnm = None
        if response := await self._api_request(
            endpoint="/v2/luaEncryption/luaGet",
            data=data
        ):
            res = await self._session.get(response["url"])
            if res.status == 200:
                lua = await res.text()
                if lua:
                    stream = ('local bit = require "bit"\n' +
                              self._security.aes_decrypt_with_fixed_key(lua))
                    stream = stream.replace("\r\n", "\n")
                    fnm = f"{path}/{response['fileName']}"
                    async with aiofiles.open(fnm, "w") as fp:
                        await fp.write(stream)
        return fnm

    async def download_plugin(
        self, path: str,
        appliance_code: str,
        smart_product_id: str,
        device_type: int,
        sn: str,
        sn8: str,
        model_number: str | None,
        manufacturer_code: str = "0000",
    ):
        return

    async def send_cloud(self, appliance_code: int, data: bytearray):
        appliance_code = str(appliance_code)
        params = {
            "clientType": "1",
            "appId": self.APP_ID,
            "format": "2",
            "deviceId": self._device_id,
            "applianceCode": appliance_code,
            'order': self._security.aes_encrypt(bytes_to_dec_string(data)).hex(),
            'timestamp': 'true',
            "isFull": "false"
        }

        if response := await self._api_request(
            endpoint='/v1/appliance/transparent/send',
            data=params,
        ):
            if response and response.get('reply'):
                _LOGGER.debug("[%s] Cloud command response: %s", appliance_code, response)
                reply_data = self._security.aes_decrypt(bytes.fromhex(response['reply']))
                return reply_data
            else:
                _LOGGER.warning("[%s] Cloud command failed: %s", appliance_code, response)

        return None

    async def get_device_status(
        self,
        appliance_code: int,
        device_type: int,
        sn: str,
        model_number: str | None,
        manufacturer_code: str = "0000",
        query: dict = {}
    ) -> dict | None:
        data = {
            "clientType": "1",
            "appId": self.APP_ID,
            "format": "2",
            "deviceId": self._device_id,
            "iotAppId": self.APP_ID,
            "applianceMFCode": manufacturer_code,
            "applianceType": "0x%02X" % device_type,
            "modelNumber": model_number,
            "applianceSn": self._security.aes_encrypt_with_fixed_key(sn.encode("ascii")).hex(),
            "version": "0",
            "encryptedType ": "2",
            "applianceCode": appliance_code,
            "command": {
                "query": query
            }
        }
        if response := await self._api_request(
            endpoint="/v1/device/status/lua/get",
            data=data
        ):
            # 预期返回形如 { ... 状态键 ... }
            return response
        return None

    async def send_device_control(
        self,
        appliance_code: int,
        device_type: int,
        sn: str,
        model_number: str | None,
        manufacturer_code: str = "0000",
        control: dict | None = None,
        status: dict | None = None
    ) -> bool:
        data = {
            "clientType": "1",
            "appId": self.APP_ID,
            "format": "2",
            "deviceId": self._device_id,
            "iotAppId": self.APP_ID,
            "applianceMFCode": manufacturer_code,
            "applianceType": "0x%02X" % device_type,
            "modelNumber": model_number,
            "applianceSn": self._security.aes_encrypt_with_fixed_key(sn.encode("ascii")).hex(),
            "version": "0",
            "encryptedType ": "2",
            "applianceCode": appliance_code,
            "command": {
                "control": control
            }
        }
        if status and isinstance(status, dict):
            data["command"]["status"] = status
        response = await self._api_request(
            endpoint="/v1/device/lua/control",
            data=data
        )
        return response is not None


def get_midea_cloud(cloud_name: str, session: ClientSession, account: str, password: str, proxy: str | None = None) -> MideaCloud | None:
    cloud = None
    if cloud_name in clouds.keys():
        cloud = globals()[clouds[cloud_name]["class_name"]](
            cloud_name=cloud_name,
            session=session,
            account=account,
            password=password,
            proxy=proxy
        )
    return cloud
