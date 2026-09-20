"""Device mapping for Midea T0x5D (制冰机 Ice Machine).

适用: MBJ-12D17ECW (sn8=333Q1669, category=ice-machine, subtype=0)
基于设备状态实体暴露的可控属性编写:
   - power_switch             电源开关
   - cleaning_switch          清洁
   - forced_deice_switch      强制除冰
   - uv_sterilization_switch  UV 杀菌
   - ice_making_mode          制冰模式（可选: 大冰 big / 小冰 small）
     * 设备以字符串上报该属性; 关机时上报 "invalid" 占位, ignore_values 过滤
   - error_type / alarm_status_identifier  故障与告警（只读）

安装: 放到 custom_components/midea_auto_cloud/device_mapping/T0x5D.py 并重启 HA。
"""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform

DEVICE_MAPPING = {
    "default": {
        "manufacturer": "Midea",
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [
            "power_switch",
            "ice_making_mode",
            "cleaning_switch",
            "forced_deice_switch",
            "uv_sterilization_switch",
        ],
        "entities": {
            Platform.SWITCH: {
                "power_switch": {
                    "name": "电源",
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "cleaning_switch": {
                    "name": "清洁",
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "forced_deice_switch": {
                    "name": "强制除冰",
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "uv_sterilization_switch": {
                    "name": "UV杀菌",
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SELECT: {
                "ice_making_mode": {
                    "name": "制冰模式",
                    "status_key": "ice_making_mode",
                    "options": {
                        "大冰": {"ice_making_mode": "big"},
                        "小冰": {"ice_making_mode": "small"},
                    },
                    "ignore_values": ["invalid"],
                },
            },
            Platform.SENSOR: {
                "error_type": {
                    "name": "故障代码",
                    "device_class": SensorDeviceClass.ENUM,
                },
                "alarm_status_identifier": {
                    "name": "告警状态",
                    "device_class": SensorDeviceClass.ENUM,
                },
            },
            Platform.BINARY_SENSOR: {
                "connected": {
                    "name": "在线",
                    "device_class": BinarySensorDeviceClass.CONNECTIVITY,
                },
            },
        },
    },
}
