"""Data coordinator for Midea Auto Cloud integration."""

import copy
import logging
import traceback
from datetime import datetime, timedelta
from typing import Any, NamedTuple

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .core.device import MiedaDevice
from .core.logger import MideaLogger

_LOGGER = logging.getLogger(__name__)

# 连续轮询失败达到该次数后，将实体标记为不可用（成功一次即恢复）
MAX_CONSECUTIVE_POLL_FAILURES = 3


class MideaDeviceData(NamedTuple):
    """Data structure for Midea device state."""
    attributes: dict
    available: bool
    connected: bool


class MideaDataUpdateCoordinator(DataUpdateCoordinator[MideaDeviceData]):
    """Data update coordinator for Midea devices."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device: MiedaDevice,
        cloud=None,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{device.device_name} ({device.device_id})",
            update_method=self.poll_device_state,
            update_interval=timedelta(seconds=device._refresh_interval),
            # Must be True: our data payload references the device's attribute
            # dict. We now emit a fresh snapshot copy each push (see _snapshot),
            # but always_update=True also guarantees listeners are refreshed on
            # every successful poll so device-side changes (e.g. made in the
            # Midea app) reliably reach HA entities.
            always_update=True,
        )
        self.device = device
        self.state_update_muted: CALLBACK_TYPE | None = None
        self._device_id = device.device_id
        self._cloud = cloud
        self._last_cloud_poll: dict[str, datetime | None] = {}
        # True while poll_device_state runs; avoid async_set_updated_data from
        # device callbacks mid-refresh (resets the poll timer and races the
        # coordinator's own listener notification).
        self._polling = False
        # E1: track last user-selected wash mode for fallback when device
        # reports neutral_gear / "" / invalid in idle state.
        self.last_user_mode: str = ""
        # 连续轮询失败计数：会话失效/设备离线时不再假装一切正常
        self._consecutive_poll_failures = 0

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        # Immediate first refresh to avoid waiting for the interval
        self.data = await self.poll_device_state()
        
        # Register for device updates
        self.device.register_update(self._device_update_callback)

    def _is_cloud_only_device(self) -> bool:
        """Return True when the device is controlled via cloud only."""
        return self.device._ip_address is None and self._cloud is not None

    @staticmethod
    def _flatten_nested_scalars(attrs: dict[str, Any]) -> None:
        """Write nested dict scalars as dotted flat keys in-place.

        Mapping presets often use ``temperature.room`` while the cloud returns
        ``{"temperature": {"room": "29.8"}}``. Expanding into the snapshot lets
        entity lookups see fresh scalars even when only nested objects change.
        """
        stack: list[tuple[str, dict]] = [
            (key, value) for key, value in list(attrs.items()) if isinstance(value, dict)
        ]
        while stack:
            prefix, node = stack.pop()
            for key, value in node.items():
                dotted = f"{prefix}.{key}"
                if isinstance(value, dict):
                    stack.append((dotted, value))
                else:
                    attrs[dotted] = value

    def _snapshot(self, available: bool | None = None) -> MideaDeviceData:
        """Build a coordinator data payload from a deep copy of device attributes.

        Critical: the device mutates self.device.attributes in place, and nested
        values (e.g. ``temperature``) are themselves dicts. A shallow
        ``dict(...)`` copy keeps sharing those nested objects with the live
        device state (and with previous snapshots), so entities can keep reading
        stale nested values even after a successful poll. Deep-copying gives
        each push an independent tree; we also expand nested scalars to dotted
        keys for stable entity lookups.
        """
        connected = self.device.connected
        if available is None:
            if self._is_cloud_only_device():
                # Cloud appliances remain controllable even when Midea reports
                # them offline at list time (onlineStatus != 1) — but repeated
                # poll failures (dead session, device offline) must surface as
                # unavailable instead of freezing entities at stale values.
                available = (
                    self._consecutive_poll_failures < MAX_CONSECUTIVE_POLL_FAILURES
                )
            else:
                available = connected
        attrs = copy.deepcopy(self.device.attributes)
        self._flatten_nested_scalars(attrs)
        return MideaDeviceData(
            attributes=attrs,
            available=available,
            connected=connected,
        )

    def mute_state_update_for_a_while(self) -> None:
        """Mute subscription for a while to avoid state bouncing."""
        if self.state_update_muted:
            self.state_update_muted()

        @callback
        def unmute(now: datetime) -> None:
            self.state_update_muted = None

        self.state_update_muted = async_call_later(self.hass, 10, unmute)

    def _auto_seed_e1_mode(self) -> None:
        """Auto-seed mode into _LOCAL_DATA for E1 dishwasher devices.

        Device-reported ``mode`` in idle state may be ``neutral_gear`` / ``""``
        / ``invalid`` — stale from a previous wash or model-dependent.  This
        seeds ``_LOCAL_DATA["mode"]`` from the real device mode (when valid)
        or falls back to ``last_user_mode`` so mode_dependent sub-feature
        entities (temperature, region, additional, etc.) stay visible and the
        start/order command receives the correct mode.
        """
        if self.device.device_type != 0xE1:
            return
        local = self.device._local_data
        if "mode" in local:
            return  # already seeded — do NOT overwrite user selection

        mode = self.device.attributes.get("mode", "")
        work_status = self.device.attributes.get("work_status", "")

        # Idle states: restore mode from device or last_user_mode
        if work_status in ("standby", "power_off", "cancel", ""):
            if not mode or mode in ("neutral_gear", "invalid"):
                if self.last_user_mode:
                    local["mode"] = self.last_user_mode
            else:
                local["mode"] = mode
        # Running states: seed real wash mode so entities reflect active cycle
        elif mode and mode not in ("neutral_gear", "invalid"):
            local["mode"] = mode

    def _device_update_callback(self, status: dict) -> None:
        """Callback for device status updates."""
        if self.state_update_muted:
            return
        
        # Update device attributes (allow new keys to be added)
        for key, value in status.items():
            self.device.attributes[key] = value

        # E1 auto-seed: ensure mode_dependent entities have a mode to work with
        self._auto_seed_e1_mode()

        # During poll_device_state the coordinator will snapshot/notify itself.
        # Pushing here would call async_set_updated_data mid-refresh and reset
        # the polling interval.
        if self._polling:
            return

        # Update coordinator data (fresh snapshot so HA detects the change)
        self.async_set_updated_data(self._snapshot())

    def _track_poll_result(self, success: bool) -> None:
        """记录轮询结果；连续失败达到阈值后标记不可用，成功一次即恢复。"""
        if success:
            if self._consecutive_poll_failures >= MAX_CONSECUTIVE_POLL_FAILURES:
                _LOGGER.warning(
                    "Device %s (%s) recovered after %s failed polls",
                    self.device.device_name,
                    self._device_id,
                    self._consecutive_poll_failures,
                )
            self._consecutive_poll_failures = 0
            return
        self._consecutive_poll_failures += 1
        if self._consecutive_poll_failures == MAX_CONSECUTIVE_POLL_FAILURES:
            _LOGGER.warning(
                "Device %s (%s) failed %s consecutive polls; "
                "marking entities unavailable until data flows again",
                self.device.device_name,
                self._device_id,
                self._consecutive_poll_failures,
            )

    async def poll_device_state(self) -> MideaDeviceData:
        """Poll device state."""
        if self.state_update_muted:
            return self.data

        refresh_ok = True
        self._polling = True
        try:
            # 检查是否为中央空调设备（T0x21）
            if self.device.device_type == 0x21:
                await self._poll_central_ac_state()
            else:
                refresh_ok = await self.device.refresh_status()
        except Exception as e:
            refresh_ok = False
            traceback.print_exc()
            _LOGGER.error(f"Error polling device state: {e}")
        finally:
            self._polling = False

        self._track_poll_result(refresh_ok)

        try:
            await self._poll_cloud_stats()
        except Exception as e:
            traceback.print_exc()
            _LOGGER.error(f"Error polling cloud stats: {e}")

        # E1 auto-seed: ensure mode_dependent entities have a mode to work with
        # after each poll cycle.
        self._auto_seed_e1_mode()

        try:
            # Return a fresh snapshot; DataUpdateCoordinator notifies listeners
            # (always_update=True). Do not call async_set_updated_data here —
            # that would nest a manual update inside an active refresh.
            return self._snapshot()
        except Exception as e:
            traceback.print_exc()
            _LOGGER.error(f"Error building device snapshot: {e}")
            return self._snapshot(available=False)
    
    async def _poll_central_ac_state(self) -> None:
        """轮询中央空调状态"""
        try:
            cloud = self._cloud
            if cloud and hasattr(cloud, "get_central_ac_status"):
                status_data = await cloud.get_central_ac_status([self._device_id])
                if status_data and "appliances" in status_data:
                    # 找到对应的设备数据并更新到设备属性中
                    for appliance in status_data["appliances"]:
                        if appliance.get("type") == "0x21" and "extraData" in appliance:
                            extra_data = appliance["extraData"]
                            if "attr" in extra_data:
                                if "nodeid" in extra_data["attr"]:
                                    self.device._attributes["nodeid"] = extra_data["attr"]["nodeid"]
                                if "masterId" in extra_data["attr"]:
                                    self.device._attributes["masterId"] = extra_data["attr"]["masterId"]
                                if "modelid" in extra_data["attr"]:
                                    self.device._attributes["modelid"] = extra_data["attr"]["modelid"]
                                if "idType" in extra_data["attr"]:
                                    self.device._attributes["idType"] = extra_data["attr"]["idType"]

                                if "state" in extra_data["attr"] and "condition_attribute" in extra_data["attr"]["state"]:
                                    state = extra_data["attr"]["state"]
                                    condition = state["condition_attribute"]
                                    # 将状态数据更新到设备属性中
                                    for key, value in condition.items():
                                        # 尝试将数字字符串转换为数字
                                        if key.find("temp") > -1:
                                            try:
                                                # 尝试转换为整数
                                                if '.' not in value:
                                                    self.device._attributes[key] = int(value)
                                                else:
                                                    # 尝试转换为浮点数
                                                    self.device._attributes[key] = float(value)
                                            except (ValueError, TypeError):
                                                # 如果转换失败，保持原值
                                                self.device._attributes[key] = value
                                        else:
                                            self.device._attributes[key] = value

                                if "endlist" in extra_data["attr"]:
                                    endlist = extra_data["attr"]["endlist"]
                                    # endlist是一个数组，包含多个endpoint对象
                                    if isinstance(endlist, list):
                                        for endpoint in endlist:
                                            if "event" in endpoint:
                                                event = endpoint["event"]
                                                endpoint_id = endpoint.get("endpoint", 1)
                                                endpoint_name = endpoint.get("name", f"按键{endpoint_id}")
                                                
                                                # 为每个endpoint创建独立的状态属性
                                                for key, value in event.items():
                                                    # 创建带endpoint标识的属性名
                                                    attr_key = f"endpoint_{endpoint_id}_{key}"
                                                    attr_name_key = f"endpoint_{endpoint_id}_name"
                                                    
                                                    # 保存endpoint名称
                                                    self.device._attributes[attr_name_key] = endpoint_name
                                                    self.device._attributes[attr_key] = value
                                                
                                                # 同时保持原有的属性名（用于兼容性）
                                                for key, value in event.items():
                                                    # 尝试将数字字符串转换为数字
                                                    self.device._attributes[key] = value

                                break
        except Exception as e:
            MideaLogger.warning(f"Error polling central AC state: {e}")

    def _cloud_poll_interval(self, query_key: str, default: int = 3600) -> int:
        cloud_queries = getattr(self.device, "_cloud_queries", None) or {}
        query_cfg = cloud_queries.get(query_key) or {}
        return int(query_cfg.get("interval", default))

    def _should_poll_cloud(self, query_key: str, now: datetime) -> bool:
        poll_interval = self._cloud_poll_interval(query_key)
        last_poll = self._last_cloud_poll.get(query_key)
        if last_poll is not None:
            elapsed = (now - last_poll).total_seconds()
            if elapsed < poll_interval:
                return False
        return True

    async def _poll_cloud_stats(self) -> None:
        """轮询云端统计（空调电量、洗衣机/洗碗机水电等）。"""
        cloud_queries = getattr(self.device, "_cloud_queries", None) or {}
        if not cloud_queries:
            return
        cloud = self._cloud
        if not cloud:
            return

        now = datetime.now()
        if cloud_queries.get("electricity") and self._should_poll_cloud("electricity", now):
            await self._poll_cloud_electricity(cloud, now)
        if cloud_queries.get("water_power") and self._should_poll_cloud("water_power", now):
            await self._poll_cloud_water_power(cloud, now, cloud_queries["water_power"])

    async def _poll_cloud_electricity(self, cloud, now: datetime) -> None:
        """轮询空调云端电量（月 + 年）。"""
        if not hasattr(cloud, "query_electricity"):
            return

        today = now.strftime("%Y-%m-%d")
        try:
            month_result = await cloud.query_electricity(
                self._device_id, query_type=2, date=today
            )
            if month_result and month_result.get("totalValue") is not None:
                self.device._attributes["cloud_electricity_month"] = float(
                    month_result["totalValue"]
                )
            elif month_result is None:
                MideaLogger.debug(
                    f"Cloud electricity month query returned no data for {self._device_id}"
                )

            year_result = await cloud.query_electricity(
                self._device_id, query_type=3, date=today
            )
            if year_result and year_result.get("totalValue") is not None:
                self.device._attributes["cloud_electricity_year"] = float(
                    year_result["totalValue"]
                )
            elif year_result is None:
                MideaLogger.debug(
                    f"Cloud electricity year query returned no data for {self._device_id}"
                )
        except Exception as e:
            MideaLogger.warning(
                f"Error polling cloud electricity for device {self._device_id}: {e}"
            )
        finally:
            self._last_cloud_poll["electricity"] = now

    def _apply_wash_cloud_totals(
        self,
        result: dict | None,
        *,
        period: str,
        dual_drum: bool,
    ) -> None:
        cloud = self._cloud
        if not cloud or not result:
            return

        drums = ("da", "db") if dual_drum else ("da", "db")
        if dual_drum:
            for drum in drums:
                water_raw = cloud._sum_wash_resource(result, drum, "water")
                power_raw = cloud._sum_wash_resource(result, drum, "power")
                self.device._attributes[f"cloud_water_{period}_{drum}"] = round(
                    cloud.wash_water_liters(water_raw), 2
                )
                self.device._attributes[f"cloud_power_{period}_{drum}"] = round(
                    cloud.wash_power_kwh(power_raw), 3
                )
        else:
            water_raw = sum(
                cloud._sum_wash_resource(result, drum, "water") for drum in drums
            )
            power_raw = sum(
                cloud._sum_wash_resource(result, drum, "power") for drum in drums
            )
            self.device._attributes[f"cloud_water_{period}"] = round(
                cloud.wash_water_liters(water_raw), 2
            )
            self.device._attributes[f"cloud_power_{period}"] = round(
                cloud.wash_power_kwh(power_raw), 3
            )

    async def _poll_cloud_water_power(
        self, cloud, now: datetime, water_power_cfg: dict
    ) -> None:
        """轮询洗衣机/洗碗机云端水电统计（月 + 年）。"""
        if not hasattr(cloud, "query_wash_water_power"):
            return

        device_type = water_power_cfg.get("device_type", self.device.device_type)
        dual_drum = bool(water_power_cfg.get("dual_drum"))
        today = now.strftime("%Y%m%d")
        try:
            month_result = await cloud.query_wash_water_power(
                self._device_id,
                device_type=device_type,
                result_type=2,
                time=today,
            )
            if month_result:
                self._apply_wash_cloud_totals(
                    month_result, period="month", dual_drum=dual_drum
                )
            else:
                MideaLogger.debug(
                    f"Cloud water/power month query returned no data for {self._device_id}"
                )

            year_result = await cloud.query_wash_water_power(
                self._device_id,
                device_type=device_type,
                result_type=3,
                time=today,
            )
            if year_result:
                self._apply_wash_cloud_totals(
                    year_result, period="year", dual_drum=dual_drum
                )
            else:
                MideaLogger.debug(
                    f"Cloud water/power year query returned no data for {self._device_id}"
                )
        except Exception as e:
            MideaLogger.warning(
                f"Error polling cloud water/power for device {self._device_id}: {e}"
            )
        finally:
            self._last_cloud_poll["water_power"] = now

    async def async_set_attribute(self, attribute: str, value) -> None:
        """Set a device attribute."""
        attributes = {}
        attributes[attribute] = value
        await self.async_set_attributes(attributes)

    async def async_set_control(self, attributes: dict) -> None:
        """Send control command directly — no optimistic local update (matching smart_home)."""
        await self.device.set_attributes(attributes)

    async def async_set_attributes(self, attributes: dict) -> None:
        """Set multiple device attributes."""
        # 云端控制：构造 control 与 status（携带当前状态作为上下文）
        # 计算逻辑使用所有属性（包括有默认值的变量）
        for c in self.device._calculate_set:
            lvalue = c.get("lvalue")
            rvalue = c.get("rvalue")
            if lvalue and rvalue:
                calculate = False
                for s, v in attributes.items():
                    if rvalue.find(f"[{s}]") >= 0:
                        calculate = True
                        break
                if calculate:
                    calculate_str1 = \
                        (f"{lvalue.replace('[', 'attributes[').replace("]", "\"]")} = "
                         f"{rvalue.replace('[', 'attributes[').replace(']', "\"]")}") \
                            .replace("[", "[\"")
                    try:
                        exec(calculate_str1)
                    except Exception as e:
                        traceback.print_exc()
                        MideaLogger.warning(
                            f"Calculation Error: {lvalue} = {rvalue}, calculate_str1: {calculate_str1}",
                            self._device_id
                        )
        
        # 冻结有默认值的变量：从发送到云端的 attributes 中移除
        attributes_to_send = {}
        for attr, value in attributes.items():
            # 如果该属性有默认值，则不发送到云端，只更新本地状态
            if attr not in self.device._default_values:
                attributes_to_send[attr] = value
        
        # 只发送没有默认值的属性到云端
        if attributes_to_send:
            if not await self.device.set_attributes(attributes_to_send):
                # 控制未送达（会话失效/设备离线）：如实报错，
                # 不做乐观镜像，避免 UI 显示一个设备从未收到的状态。
                _LOGGER.warning(
                    "Failed to send control to %s (%s): %s",
                    self.device.device_name,
                    self._device_id,
                    attributes_to_send,
                )
                raise HomeAssistantError(
                    f"Failed to send command to Midea device "
                    f"{self.device.device_name} ({self._device_id})"
                )
            # 控制送达说明云端会话与设备均正常，清零失败计数
            self._track_poll_result(True)
        # 更新所有属性到本地状态（包括有默认值的变量）
        self.device.attributes.update(attributes)
        self.mute_state_update_for_a_while()
        # Push a fresh snapshot so the optimistic value lands in coordinator.data
        # (entities read coordinator.data.attributes, which is now a copy).
        self.async_set_updated_data(self._snapshot())

    async def async_send_command(self, cmd_type: int, cmd_body: str) -> None:
        """Send a command to the device."""
        try:
            cmd_body_bytes = bytearray.fromhex(cmd_body)
            await self.device.send_command(cmd_type, cmd_body_bytes)
        except ValueError as e:
            _LOGGER.error(f"Invalid command body: {e}")
            raise

    async def async_send_central_ac_control(self, control: dict) -> bool:
        """发送中央空调控制命令"""
        try:
            cloud = self._cloud
            if cloud and hasattr(cloud, "send_central_ac_control"):
                # 从设备属性中获取nodeid
                masterid = self.device.attributes.get("masterId")
                nodeid = self.device.attributes.get("nodeid")
                modelid = self.device.attributes.get("modelid")
                idtype = int(self.device.attributes.get("idType"))

                if not nodeid:
                    MideaLogger.warning(f"No nodeid found for central AC device {self._device_id}")
                    return False
                
                # 构建完整的控制命令，包含centralized中的所有字段
                full_control = self._build_full_central_ac_control(control)
                MideaLogger.debug(f"Sending control to {self.device.device_name}: {full_control}")
                success = await cloud.send_central_ac_control(
                    masterid,
                    nodeid,
                    modelid,
                    idtype,
                    full_control
                )

                if success:
                    # 更新本地状态
                    self.device.attributes.update(control)
                    self.mute_state_update_for_a_while()
                    self.async_set_updated_data(self._snapshot())
                    return True
                else:
                    MideaLogger.warning(f"Failed to send control to {self.device.device_name}")
                    return False
            else:
                MideaLogger.warning("Cloud service not available for central AC control")
                return False
        except Exception as e:
            MideaLogger.warning(f"Error sending control to {self.device.device_name}: {e}")
            return False

    async def async_send_switch_control(self, control: dict) -> bool:
        """发送开关控制命令（subtype为00000000的设备）"""
        try:
            cloud = self._cloud
            if cloud and hasattr(cloud, "send_switch_control"):
                # 获取设备ID和nodeId
                masterid = str(self.device.attributes.get("masterId"))
                nodeid = str(self.device.attributes.get("nodeid"))
                
                if not nodeid:
                    MideaLogger.warning(f"No nodeid found for switch device {self._device_id}")
                    return False
                
                # 根据控制命令确定endPoint和attribute值
                end_point = control.get("endpoint", 1)  # 从control中获取endpoint，默认1
                attribute = 0  # 默认attribute
                
                # 根据control内容设置attribute值
                if "run_mode" in control:
                    if control["run_mode"] == "1":
                        attribute = 1  # 开启
                    else:
                        attribute = 0  # 关闭
                
                # 构建控制数据
                switch_control = {
                    "endPoint": end_point,
                    "attribute": attribute
                }
                
                MideaLogger.debug(f"Sending switch control to {self.device.device_name}: {switch_control}")
                success = await cloud.send_switch_control(masterid, nodeid, switch_control)
                
                if success:
                    # 更新本地状态 - 使用类似poll_central的解析方法
                    await self._update_switch_status_from_control(control)
                    self.mute_state_update_for_a_while()
                    self.async_set_updated_data(self._snapshot())
                    return True
                else:
                    MideaLogger.warning(f"Failed to send switch control to {self.device.device_name}")
                    return False
            else:
                MideaLogger.warning("Cloud service not available for switch control")
                return False
        except Exception as e:
            MideaLogger.warning(f"Error sending switch control to {self.device.device_name}: {e}")
            return False

    async def _update_switch_status_from_control(self, control: dict) -> None:
        """根据控制命令更新开关状态，参照poll_central的解析方法"""
        try:
            # 获取endpoint ID
            endpoint_id = control.get("endpoint", 1)
            run_mode = control.get("run_mode", "0")
            
            # 模拟endlist数据结构来更新状态
            # 根据run_mode设置OnOff状态
            onoff_value = "1" if run_mode == "1" else "0"
            
            # 更新endpoint特定的状态属性
            attr_key = f"endpoint_{endpoint_id}_OnOff"
            self.device._attributes[attr_key] = onoff_value
            
            # 同时更新兼容性属性
            self.device._attributes["OnOff"] = onoff_value
            
            # MideaLogger.debug(f"Updated switch status for endpoint {endpoint_id}: OnOff={onoff_value}")
            
        except Exception as e:
            MideaLogger.warning(f"Error updating switch status from control: {e}")

    def _build_full_central_ac_control(self, new_control: dict) -> dict:
        """构建完整控制命令"""
        full_control = {}
        full_control["run_mode"] = self.device.attributes.get("run_mode")
        full_control["cooling_temp"] = str(self.device.attributes.get("cool_temp_set") or 26.0)
        full_control["heating_temp"] = str(self.device.attributes.get("heat_temp_set") or 20.0)
        full_control["fan_speed"] = self.device.attributes.get("fan_speed")
        swing_mode = self.device.attributes.get("is_swing")
        is_elec_heat = self.device.attributes.get("is_elec_heat")

        if swing_mode == "1":
            # 开启摆风：如果当前有电辅热(2)，则设为6(电辅热+摆风)，否则设为4(摆风)
            if is_elec_heat == "1":
                new_extflag = "6"  # 电辅热+摆风
            else:
                new_extflag = "4"  # 仅摆风
        else:
            # 关闭摆风：如果当前是6(电辅热+摆风)，则设为2(仅电辅热)，否则设为0(关闭)
            if is_elec_heat == "1":
                new_extflag = "2"  # 仅电辅热
            else:
                new_extflag = "0"  # 关闭

        full_control["extflag"] = new_extflag

        # 然后用新的控制值覆盖
        full_control.update(new_control)
        return full_control