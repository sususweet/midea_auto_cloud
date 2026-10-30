"""Staged microwave controls for Midea BF/700006DJ (GR6 Pro, subtype 5)."""

import asyncio
from copy import deepcopy
from typing import TYPE_CHECKING

from homeassistant.const import Platform, UnitOfTime
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from .data_coordinator import MideaDataUpdateCoordinator

SECONDS = "gr6_microwave_seconds"
POWER = "gr6_microwave_power"
POWER_LEVELS = {
    "低": "fire_power_1",
    "中低": "fire_power_3",
    "中": "fire_power_5",
    "中高": "fire_power_8",
    "高": "fire_power_10",
}
_CONTROL_LOCK = asyncio.Lock()


def add_gr6_pro_mapping(mappings: dict) -> None:
    """Keep upstream sensors and add controls only for this product."""
    config = deepcopy(mappings["default"])
    config["entities"][Platform.NUMBER] = {
        SECONDS: {
            "name": "微波时长（待启动）",
            "min": 5,
            "max": 1795,
            "step": 5,
            "mode": "box",
            "unit_of_measurement": UnitOfTime.SECONDS,
            "default_value": None,
        }
    }
    config["entities"][Platform.SELECT] = {
        POWER: {
            "name": "微波火力（待启动）",
            "options": {label: {POWER: value} for label, value in POWER_LEVELS.items()},
            "default_value": None,
        }
    }
    config["entities"][Platform.BUTTON] = {
        f"gr6_{action}": {"name": name, "gr6_pro_action": action}
        for action, name in (
            ("start_microwave", "开始微波"),
            ("pause", "暂停烹饪"),
            ("resume", "继续烹饪"),
            ("cancel", "取消烹饪"),
        )
    }
    # Never centralize work_mode: adding it to pause/cancel would start cooking.
    config["centralized"] = []
    mappings["700006DJ"] = config


def microwave_command(attributes: dict) -> dict:
    """Validate explicitly selected settings and build one cooking command."""
    value = attributes.get(SECONDS)
    if isinstance(value, bool):
        raise HomeAssistantError("请先设置微波时长：5 秒到 29 分 55 秒，步长 5 秒")
    try:
        seconds = float(value)
    except (TypeError, ValueError) as err:
        raise HomeAssistantError("请先设置微波时长") from err
    if not 5 <= seconds <= 1795 or seconds % 5:
        raise HomeAssistantError("微波时长须为 5 秒到 29 分 55 秒，步长 5 秒")
    power = attributes.get(POWER)
    if power not in POWER_LEVELS.values():
        raise HomeAssistantError("请先选择微波火力")
    minutes, seconds = divmod(int(seconds), 60)
    return {
        "work_mode": "microwave_1",
        "work_hour": 0,
        "work_minute": minutes,
        "work_second": seconds,
        "fire_power": power,
        "pre_heat": "off",
    }


async def _refresh(coordinator: "MideaDataUpdateCoordinator") -> None:
    device = coordinator.device
    # refresh_status otherwise treats previously skipped queries as success.
    success = not device._skipped_queries and await device.refresh_status()
    coordinator._track_poll_result(bool(success))
    coordinator.async_set_updated_data(
        coordinator._snapshot(available=None if success else False)
    )
    if not success:
        raise HomeAssistantError("无法取得设备最新状态；请在本机确认，勿连续重试")


async def async_execute(
    coordinator: "MideaDataUpdateCoordinator", action: str
) -> None:
    """Send only an explicit button action, with fresh-state checks."""
    device = coordinator.device
    if (
        device.device_type != 0xBF
        or device.sn8 != "700006DJ"
        or str(device.subtype) != "5"
    ):
        raise HomeAssistantError("此控制适配仅适用于已核验的 GR6 Pro 型号")
    if action not in {"start_microwave", "pause", "resume", "cancel"}:
        raise HomeAssistantError(f"不支持的 GR6 Pro 操作：{action}")

    async with _CONTROL_LOCK:
        command = (
            microwave_command(dict(device.attributes))
            if action == "start_microwave"
            else {"work_status": {"pause": "pause", "resume": "work", "cancel": "standby"}[action]}
        )
        await _refresh(coordinator)
        attributes = device.attributes
        status = attributes.get("work_status")
        allowed = {
            "start_microwave": {"standby", "save_power", "work_finish"},
            "pause": {"work"},
            "resume": {"pause", "pause_c"},
            "cancel": {"work", "pause", "pause_c", "order"},
        }
        if status not in allowed[action]:
            raise HomeAssistantError(f"当前工作状态不允许此操作：{status}")
        if action in {"start_microwave", "resume"}:
            if attributes.get("door_open") != "off":
                raise HomeAssistantError("请确认炉门已关好，且门状态可读")
            if attributes.get("lock") != "off":
                raise HomeAssistantError("请先在本机解除童锁，且童锁状态须可读")
            if attributes.get("error_code") not in (0, "0"):
                raise HomeAssistantError("设备故障状态异常或未知，请先在本机检查")

        # Bypass optimistic state mirroring; confirm the actual appliance response.
        if not await device.set_attributes(command):
            raise HomeAssistantError("命令发送结果未确认；请在本机检查，勿连续重试")
        result = device.attributes.get("execute")
        if result != "ok":
            raise HomeAssistantError(f"设备未确认接受命令：{result}")
        expected = {
            "start_microwave": {"work", "work_finish"},
            "pause": {"pause", "pause_c"},
            "resume": {"work", "work_finish"},
            "cancel": {"standby", "save_power", "work_finish"},
        }
        for attempt in range(3):
            await _refresh(coordinator)
            attributes = device.attributes
            if (
                attributes.get("work_status") in expected[action]
                and (
                    action != "start_microwave"
                    or attributes.get("work_mode") == "microwave_1"
                )
            ):
                return
            if attempt < 2:
                await asyncio.sleep(1)
        raise HomeAssistantError("命令已发送，但未确认预期状态；请在本机检查，勿连续重试")
