import logging
import asyncio
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
from .util import bytes_to_dec_string, dec_string_to_bytes

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

# 重新登录节流：一次登录尝试失败后，至少间隔该秒数才允许下一次尝试，避免登录风暴
RELOGIN_RETRY_COOLDOWN = 60

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
        # 发生 token 失效时，避免每次请求都触发重复登录
        self._token_invalid_retry_count = 0
        self._relogin_lock = asyncio.Lock()
        # token 失效（如 40002 user token not exist）时自动重新登录并重试请求
        self._auto_relogin_on_token_invalid = True
        # 最近一次重新登录尝试的时间（monotonic），用于节流
        self._last_relogin_attempt = float("-inf")
        # 正在执行 login() 的任务，用于避免登录流程内部的请求递归触发重登（死锁）
        self._relogin_task: asyncio.Task | None = None
        self._on_login_success = None
        # 仅 /status/lua/get 可能返回 1014 lua analysis exception
        self._lua_status_analysis_error = False
        self._lua_status_analysis_msg: str | None = None

    def _make_general_data(self):
        return {}

    @staticmethod
    def _redact_for_log(header: dict | None) -> dict:
        """日志中脱敏用户 token，避免明文落盘。"""
        if not header:
            return {}
        redacted = dict(header)
        for key in ("accesstoken", "accessToken", "access_token", "Authorization"):
            if key in redacted and redacted[key]:
                redacted[key] = "***"
        return redacted

    @property
    def nickname(self):
        """获取用户昵称"""
        # 确保_nickname属性存在
        if not hasattr(self, "_nickname"):
            self._nickname = self._account
        return self._nickname

    @property
    def lua_status_analysis_error(self) -> bool:
        """最近一次 status/lua/get 是否因 lua 解析异常失败。"""
        return self._lua_status_analysis_error

    @property
    def lua_status_analysis_msg(self) -> str | None:
        return self._lua_status_analysis_msg

    @staticmethod
    def _is_lua_status_endpoint(endpoint: str) -> bool:
        return "status/lua/get" in endpoint

    @staticmethod
    def _is_lua_analysis_response(response: dict) -> bool:
        try:
            code = int(response.get("code", -1))
        except Exception:
            code = -1
        if code == 1014:
            return True
        msg = str(response.get("msg") or response.get("message") or "").lower()
        return "lua analysis exception" in msg

    @staticmethod
    def _is_login_endpoint(endpoint: str) -> bool:
        """登录流程自身使用的接口：不参与自动重登/计数清零，避免递归与死锁。"""
        return "/user/login" in endpoint or "/unitcenter/router/" in endpoint

    async def _ensure_logged_in(self) -> bool:
        """访问令牌缺失时自动重新登录（带节流）。

        会话失效后若当场重登失败（如云端瞬时故障返回非 JSON），旧实现不会再有
        任何登录重试，集成会永久停留在未登录状态：轮询与控制全部静默失败。
        这里在每次业务请求前补一次登录机会，保证会话可自愈。
        """
        if self._access_token is not None:
            return True
        if self._relogin_task is asyncio.current_task():
            # login() 流程内部的嵌套请求，直接放行，避免对自身锁死锁
            return False
        async with self._relogin_lock:
            if self._access_token is not None:
                return True
            now = time.monotonic()
            if now - self._last_relogin_attempt < RELOGIN_RETRY_COOLDOWN:
                return False
            self._last_relogin_attempt = now
            self._relogin_task = asyncio.current_task()
            try:
                MideaLogger.warning("Midea cloud session已丢失，尝试自动重新登录。")
                if await self.login():
                    self._token_invalid_retry_count = 0
                    MideaLogger.warning("Midea cloud 自动重新登录成功。")
                    return True
                MideaLogger.warning(
                    f"Midea cloud 自动重新登录失败，{RELOGIN_RETRY_COOLDOWN}秒后随下次请求重试。"
                )
                return False
            except Exception:
                traceback.print_exc()
                return False
            finally:
                self._relogin_task = None

    @staticmethod
    def _is_token_invalid_response(response: dict) -> bool:
        try:
            code = int(response.get("code", -1))
        except Exception:
            code = -1
        if code == 40002:
            return True
        msg = str(response.get("msg") or response.get("message") or "")
        msg_lower = msg.lower()
        return (
            code in (7400, 40002)
            or "user token not exist" in msg_lower
            or "user does not exist" in msg_lower
            or ("token" in msg_lower and "not exist" in msg_lower)
            or "token校验不通过" in msg
        )

    async def _api_request(
        self,
        endpoint: str,
        data: dict,
        header=None,
        method="POST",
        _retried_after_login: bool = False,
        print_log: bool = False,
    ) -> dict | None:
        header = header or {}
        if not data.get("reqId"):
            data.update({
                "reqId": token_hex(16)
            })
        if not data.get("stamp"):
            data.update({
                "stamp":  datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            })
        # 会话已丢失（如重登失败后）时先尝试恢复登录，修复“登录失败后永不重试”的死状态
        if (
            self._auto_relogin_on_token_invalid
            and self._access_token is None
            and not _retried_after_login
            and not self._is_login_endpoint(endpoint)
        ):
            await self._ensure_logged_in()
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
        is_lua_status = self._is_lua_status_endpoint(endpoint)
        if is_lua_status:
            self._lua_status_analysis_error = False
            self._lua_status_analysis_msg = None
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
            MideaLogger.debug(
                f"Midea cloud API url: {url}, header: {self._redact_for_log(header)}, "
                f"data: {data}, response: {raw}"
            )
            response = json.loads(raw)
        except Exception as e:
            traceback.print_exc()

        if int(response["code"]) == 0:
            # 业务请求成功即可清零计数；登录流程自身的 code==0 不算
            # （login() 过程中也会返回 code==0，若计入会把计数过早重置）。
            if _retried_after_login or not self._is_login_endpoint(endpoint):
                self._token_invalid_retry_count = 0
            if "data" in response:
                return response["data"]
            else:
                return {"message": "ok"}

        # 仅 status/lua/get 会出现 lua analysis exception，标记后供调用方跳过重试
        if is_lua_status and self._is_lua_analysis_response(response):
            self._lua_status_analysis_error = True
            self._lua_status_analysis_msg = response.get("msg") or response.get("message")
            return None

        # 关闭自动重登时，不做 token 失效专项检测与日志记录，按普通失败返回
        if (
            self._auto_relogin_on_token_invalid
            and not _retried_after_login
            and not self._is_login_endpoint(endpoint)
            and self._relogin_task is not asyncio.current_task()
            and isinstance(response, dict)
            and self._is_token_invalid_response(response)
        ):
            if self._token_invalid_retry_count >= 3:
                if time.monotonic() - self._last_relogin_attempt < RELOGIN_RETRY_COOLDOWN:
                    MideaLogger.warning(
                        "Midea cloud token失效重试次数过多，冷却期内跳过登录重试。"
                        f"endpoint={endpoint}, retry_count={self._token_invalid_retry_count}"
                    )
                    return None
                # 冷却期已过：重置计数继续尝试，避免永久放弃登录
                self._token_invalid_retry_count = 0
            self._token_invalid_retry_count += 1
            MideaLogger.warning(f"Midea cloud token失效，准备重新登录后重试请求。endpoint={endpoint}, retry_count={self._token_invalid_retry_count}, code={response.get('code')}, msg={response.get('msg') or response.get('message')}")
            self._access_token = None
            try:
                async with self._relogin_lock:
                    if self._access_token is None:
                        if time.monotonic() - self._last_relogin_attempt < RELOGIN_RETRY_COOLDOWN:
                            return None
                        self._last_relogin_attempt = time.monotonic()
                        self._relogin_task = asyncio.current_task()
                        try:
                            if not await self.login():
                                return None
                        finally:
                            self._relogin_task = None
                return await self._api_request(
                    endpoint=endpoint,
                    data=data,
                    header=header,
                    method=method,
                    _retried_after_login=True,
                    print_log=print_log,
                )
            except Exception:
                traceback.print_exc()
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


    def set_login_success_callback(self, callback):
        self._on_login_success = callback

    async def _notify_login_success(self):
        callback = self._on_login_success
        if callback is None:
            return
        try:
            result = callback(self)
            if asyncio.iscoroutine(result):
                await result
        except Exception:
            traceback.print_exc()

    def export_session_payload(self) -> dict:
        payload = {
            "schema": "midea_cloud_session_v1",
            "cloud_type": self.__class__.__name__,
            "account": self._account,
            "server": None,
            "access_token": self._access_token,
            "uid": "",
            "aes_key": self._security._aes_key.decode("ascii") if getattr(self._security, "_aes_key", None) else None,
            "aes_iv": self._security._aes_iv.decode("ascii") if getattr(self._security, "_aes_iv", None) else None,
            "device_id": self._device_id,
            "updated_at": int(time.time()),
        }
        return payload
    def import_session_payload(self, payload: dict):
        self._access_token = payload.get("access_token")
        aes_key = payload.get("aes_key")
        aes_iv = payload.get("aes_iv")
        if aes_key:
            # export_session_payload() stores the *already-decrypted* AES key/iv
            # (self._security._aes_key/_aes_iv). Restore them directly. Do NOT
            # route them back through set_aes_keys(): on the MSmart cloud that
            # override expects the *encrypted* values and would try to decrypt our
            # plaintext again, raising "Data must be padded to 16 byte boundary
            # in CBC" and aborting the session restore.
            self._security._aes_key = aes_key.encode("ascii")
            self._security._aes_iv = aes_iv.encode("ascii") if aes_iv else None


    async def login(self) -> bool:
        raise NotImplementedError()

    async def list_home(self) -> dict | None:
        return None

    async def list_appliances(self, home_id) -> dict | None:
        raise NotImplementedError()

    async def download_lua(
            self, path: str,
            device_type: int,
            sn: str,
            model_number: str | None,
            manufacturer_code: str = "0000",
            smart_product_id: str = None,
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
                data=data,
            ):
                self._access_token = response["mdata"]["accessToken"]
                self._security.set_aes_keys(
                    self._security.aes_decrypt_with_fixed_key(
                        response["key"]
                    ), None
                )
                # 获取用户昵称
                if "userInfo" in response and "nickName" in response["userInfo"]:
                    self._nickname = response["userInfo"]["nickName"]
                else:
                    self._nickname = self._account
                await self._notify_login_success()
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
                            "category": appliance.get("category"),
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
            data=params
        ):
            if response and response.get('reply'):
                reply_data = self._security.aes_decrypt(bytes.fromhex(response['reply']))
                MideaLogger.debug(f"[{appliance_code}] Cloud command response: {dec_string_to_bytes(reply_data).hex()}")
                return reply_data
            else:
                MideaLogger.warning(f"[{appliance_code}] Cloud command failed: {response}")

        return None

    async def _jykt_api_request(
        self,
        endpoint: str,
        data: dict,
        header=None,
        _retried_after_login: bool = False,
    ) -> dict | None:
        """家用空调 jykt 接口，响应格式为 errCode/result 而非 code/data。"""
        header = header or {}
        # 会话已丢失时先尝试恢复登录（带节流），与 _api_request 保持一致
        if (
            self._auto_relogin_on_token_invalid
            and self._access_token is None
            and not _retried_after_login
        ):
            await self._ensure_logged_in()
        random = str(int(time.time() * 1000))
        url = self._api_url + endpoint
        dump_data = json.dumps(data)
        sign = self._security.sign(dump_data, random)
        header.update({
            "content-type": "application/json",
            "secretVersion": "1",
            "sign": sign,
            "random": random,
        })
        if self._access_token is not None:
            header.update({
                "accesstoken": self._access_token
            })
        response: dict = {}
        try:
            r = await self._session.request(
                "POST",
                url,
                headers=header,
                data=dump_data,
                timeout=30,
                proxy=self._proxy,
            )
            raw = await r.read()
            MideaLogger.debug(
                f"Midea jykt API url: {url}, data: {data}, response: {raw}"
            )
            response = json.loads(raw)
        except Exception:
            traceback.print_exc()
            return None

        if str(response.get("errCode")) == "0":
            if _retried_after_login:
                self._token_invalid_retry_count = 0
            return response.get("result")

        err_code = response.get("errCode")
        err_msg = response.get("errMsg") or response.get("message")
        if err_code is not None:
            MideaLogger.debug(
                f"Midea jykt API failed: endpoint={endpoint}, "
                f"errCode={err_code}, errMsg={err_msg}, data={data}"
            )

        # 关闭自动重登时，不做 token 失效专项检测与日志记录
        if (
            self._auto_relogin_on_token_invalid
            and not _retried_after_login
            and self._relogin_task is not asyncio.current_task()
            and isinstance(response, dict)
            and self._is_token_invalid_response(response)
        ):
            if self._token_invalid_retry_count >= 3:
                if time.monotonic() - self._last_relogin_attempt < RELOGIN_RETRY_COOLDOWN:
                    MideaLogger.warning(
                        "Midea cloud token失效重试次数过多，冷却期内跳过登录重试。"
                        f"endpoint={endpoint}, retry_count={self._token_invalid_retry_count}"
                    )
                    return None
                # 冷却期已过：重置计数继续尝试，避免永久放弃登录
                self._token_invalid_retry_count = 0
            self._token_invalid_retry_count += 1
            self._access_token = None
            try:
                async with self._relogin_lock:
                    if self._access_token is None:
                        if time.monotonic() - self._last_relogin_attempt < RELOGIN_RETRY_COOLDOWN:
                            return None
                        self._last_relogin_attempt = time.monotonic()
                        self._relogin_task = asyncio.current_task()
                        try:
                            if not await self.login():
                                return None
                        finally:
                            self._relogin_task = None
                return await self._jykt_api_request(
                    endpoint=endpoint,
                    data=data,
                    header=header,
                    _retried_after_login=True,
                )
            except Exception:
                traceback.print_exc()
        return None

    async def query_electricity(
        self,
        appliance_id: int,
        query_type: int = 2,
        date: str | None = None,
    ) -> dict | None:
        """查询空调云端电量统计。type: 1=周, 2=月, 3=年。"""
        if date is None:
            date = datetime.date.today().strftime("%Y-%m-%d")
        return await self._jykt_api_request(
            "/jykt/bluetooth/control/queryElec",
            {
                "applianceId": str(appliance_id),
                "type": query_type,
                "date": date,
            },
        )

    @staticmethod
    def _normalize_wash_device_type(device_type: int | str) -> str:
        if isinstance(device_type, int):
            return f"{device_type:02X}"
        value = str(device_type).upper()
        if value.startswith("T0X"):
            return value[3:]
        if value.startswith("0X"):
            return value[2:]
        return value

    @staticmethod
    def _sum_wash_resource(result: dict | None, drum: str, resource: str) -> float:
        if not result:
            return 0.0
        entries = ((result.get(drum) or {}).get(resource)) or []
        total = 0.0
        for entry in entries:
            try:
                total += float(entry.get("amount") or 0)
            except (TypeError, ValueError):
                continue
        return total

    @staticmethod
    def wash_water_liters(amount: float) -> float:
        """云端水量原始值单位为 mL。"""
        return amount / 1000.0

    @staticmethod
    def wash_power_kwh(amount: float) -> float:
        """云端电量原始值单位为 0.0001 kWh。"""
        return amount / 10000.0

    async def query_wash_water_power(
        self,
        appliance_id: int,
        device_type: int | str,
        result_type: int = 2,
        time: str | None = None,
        expend_type: int = 3,
    ) -> dict | None:
        """查询洗衣机/洗碗机云端水电统计。

        result_type: 1=日, 2=月, 3=年。
        """
        if time is None:
            time = datetime.date.today().strftime("%Y%m%d")
        device_type_hex = self._normalize_wash_device_type(device_type)
        endpoint = (
            f"/xyj/h5/api/WashSessions/getWaterPower"
            f"&applianceId={appliance_id}"
            f"&time={time}"
            f"&resultType={result_type}"
            f"&expendType={expend_type}"
            f"&deviceType={device_type_hex}"
        )
        return await self._jykt_api_request(endpoint, {})

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

    async def get_user_info(self):
        """获取用户信息"""
        data = {}
        if response := await self._api_request(
            endpoint="/v1/user/info/get",
            data=data
        ):
            MideaLogger.debug(f"Get user info response keys: {list(response.keys())}")
            # 检查响应结构
            if "data" in response:
                MideaLogger.debug(f"Get user info data keys: {list(response['data'].keys())}")
                if "userInfo" in response['data']:
                    MideaLogger.debug(f"Get user info userInfo keys: {list(response['data']['userInfo'].keys())}")
                    return response['data']['userInfo']
            # 直接返回响应
            return response
        return None

    async def download_lua(
            self, path: str,
            device_type: int,
            sn: str,
            model_number: str | None,
            manufacturer_code: str = "0000",
            smart_product_id: str = None
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
        # 先尝试获取文件名，检查文件是否存在
        if response := await self._api_request(
            endpoint="/v1/appliance/protocol/lua/luaGet",
            data=data
        ):
            fnm = f"{path}/{response['fileName']}"
            # 检查文件是否已经存在
            if os.path.exists(fnm):
                MideaLogger.debug(f"Lua file already exists: {fnm}, skipping download")
                return fnm
            # 文件不存在，下载
            res = await self._session.get(response["url"])
            if res.status == 200:
                lua = await res.text()
                if lua:
                    stream = ('local bit = require "bit"\n' +
                              self._security.aes_decrypt_with_fixed_key(lua))
                    stream = stream.replace("\r\n", "\n")
                    async with aiofiles.open(fnm, "w", encoding="utf-8") as fp:
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
            
            # 检查文件是否已经存在
            fnm = f"{path}/{zip_title}"
            if os.path.exists(fnm):
                MideaLogger.debug(f"Plugin file already exists: {fnm}, skipping download")
                return fnm
            
            try:
                # 确保目录存在
                os.makedirs(path, exist_ok=True)
                
                res = await self._session.get(zip_url)
                if res.status == 200:
                    zip_data = await res.read()
                    if zip_data:
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

    async def download_device_config(self, sn8: str, device_type: int) -> dict | None:
        """Download per-model device configuration from cloud (getAppModelConfig)."""
        import hashlib
        import hmac

        iot_key = clouds["美的美居"]["iot_key"]
        hmac_key = clouds["美的美居"]["hmac_key"]

        config_data = {
            "msg": "getAppModelConfig",
            "params": {
                "protype": f"{device_type:x}",
                "sn8": sn8,
            },
            "reqId": token_hex(16),
            "stamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        }
        json_data = json.dumps(config_data, separators=(',', ':'))
        random = str(int(time.time()))
        msg = iot_key + json_data + random
        sign = hmac.new(hmac_key.encode("ascii"), msg.encode("ascii"), hashlib.sha256).hexdigest()

        headers = {
            "content-type": "application/json; charset=utf-8",
            "secretVersion": "1",
            "accesstoken": self._access_token,
            "random": random,
            "sign": sign,
        }
        url = self._api_url + "/cfhrs/common/v1/api"
        try:
            r = await self._session.request(
                "POST", url, headers=headers, data=json_data,
                timeout=30, proxy=self._proxy,
            )
            raw = await r.read()
            MideaLogger.debug(
                f"download_device_config url: {url}, response: {raw}"
            )
            result = json.loads(raw)
        except Exception as e:
            MideaLogger.warning(f"download_device_config exception: {e}")
            return None

        if not isinstance(result, dict) or not result:
            return None

        ret_code = str(result.get("retCode", result.get("code", "-1")))
        if ret_code != "0":
            return None

        data = result.get("data") or result.get("result") or {}
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return None
        if "config" in data:
            config = data["config"]
        elif "result" in data and "config" in data["result"]:
            config = data["result"]["config"]
        else:
            config = data

        if isinstance(config, str):
            try:
                config = json.loads(config)
            except json.JSONDecodeError:
                return None
        return config if isinstance(config, dict) else None

    async def download_diff_config(self, device_type: int) -> dict | None:
        """Download global diff config (sn8='DIFFTYPE')."""
        return await self.download_device_config("DIFFTYPE", device_type)

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
        self._homegroup_id = None

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

    def export_session_payload(self) -> dict:
        payload = super().export_session_payload()
        payload.update({
            "uid": self._uid,
            "api_url": self._api_url,
        })
        return payload

    def import_session_payload(self, payload: dict):
        super().import_session_payload(payload)
        self._uid = payload.get("uid") or ""
        if api_url := payload.get("api_url"):
            self._api_url = api_url

    async def _api_request(self,
        endpoint: str,
        data: dict,
        header=None,
        method="POST",
        _retried_after_login: bool = False,
        print_log: bool = False
    ) -> dict | None:
        header = header or {}
        header.update({
            "x-recipe-app": self.APP_ID,
            "authorization": f"Basic {self._auth_base}"
        })
        if len(self._uid) > 0:
            header.update({
                "uid": self._uid
            })
        # 必须透传 method 与 _retried_after_login：
        # 丢失 _retried_after_login 会让基类的“重试成功后清零计数”永远不生效，
        # token 失效计数只增不减，累计 3 次后自动重登被永久跳过。
        return await super()._api_request(
            endpoint,
            data,
            header,
            method=method,
            _retried_after_login=_retried_after_login,
            print_log=True,
        )

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
                data=data,
            ):
                self._uid = response["uid"]
                self._access_token = response["mdata"]["accessToken"]
                self._security.set_aes_keys(response["accessToken"], response["randomData"])
                # 获取用户昵称
                if "userInfo" in response and "nickName" in response["userInfo"]:
                    self._nickname = response["userInfo"]["nickName"]
                else:
                    self._nickname = self._account
                await self._notify_login_success()
                return True
        return False

    async def list_home(self):
        data = self._make_general_data()
        if response := await self._api_request(
            endpoint="/v1/homegroup/list/get",
            data=data,
        ):
            homes = {}
            for home in response.get("homeList") or []:
                homes[int(home["homegroupId"])] = home.get("homeName") or home["homeName"]
            return homes if homes else None

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
                    "category": appliance.get("category"),
                    "model_number": appliance.get("modelNumber", "0"),
                    "manufacturer_code": appliance.get("enterpriseCode", "0000"),
                    "model": "",
                    "online": appliance.get("onlineStatus") == "1",
                    "smart_product_id": appliance.get("smartProductId"),
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
        smart_product_id: str = None
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
            "encryptedType ": "2",
        }
        if smart_product_id:
            data.update({"smartProductId": smart_product_id})
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
                    async with aiofiles.open(fnm, "w", encoding="utf-8") as fp:
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
            print_log=True,
        ):
            if response and response.get('reply'):
                MideaLogger.debug(f"[{appliance_code}] Cloud command response: {response}")
                reply_data = self._security.aes_decrypt(bytes.fromhex(response['reply']))
                return reply_data
            else:
                MideaLogger.warning(f"[{appliance_code}] Cloud command failed: {response}")

        return None

    async def get_user_info(self):
        """获取用户信息"""
        data = self._make_general_data()
        if response := await self._api_request(
            endpoint="/v1/user/info/get",
            data=data
        ):
            MideaLogger.debug(f"Get user info response: {response}")
            return response
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
