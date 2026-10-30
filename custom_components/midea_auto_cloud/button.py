from homeassistant.components.button import ButtonEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from .platform_setup import async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities for Midea devices."""
    await async_setup_platform_entities(
        hass,
        config_entry,
        async_add_entities,
        Platform.BUTTON,
        lambda coordinator, device, manufacturer, rationale, entity_key, ecfg: MideaButtonEntity(
            coordinator, device, manufacturer, rationale, entity_key, ecfg
        ),
    )


class MideaButtonEntity(MideaEntity, ButtonEntity):
    """Midea button entity."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        super().__init__(
            coordinator,
            device.device_id,
            device.device_name,
            f"T0x{device.device_type:02X}",
            device.sn,
            device.sn8,
            device.model,
            entity_key,
            device=device,
            manufacturer=manufacturer,
            rationale=rationale,
            config=config,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        self._require_command_condition()
        prepare = self._config.get("prepare_command")
        if prepare and self._check_condition(prepare["condition"]):
            await self.async_set_attributes(prepare["command"])
        prepare = {}
        for wire_key, attribute in self._config.get("prepare_attributes", {}).items():
            value = self._get_nested_value(attribute)
            if value is None:
                raise HomeAssistantError("Select the required duration before starting")
            prepare[wire_key] = value
        if prepare:
            await self.async_set_attributes(prepare)
            if any(self._get_nested_value(key) != value for key, value in prepare.items()):
                raise HomeAssistantError("Duration was not confirmed; operation was not started")
        # 从配置中获取要执行的命令或操作
        command = self._config.get("command")
        attribute = self._config.get("attribute", self._entity_key)
        value = self._config.get("value")
        
        # 判断是否为中央空调设备（T0x21）
        is_central_ac = self._device.device_type == 0x21 if self._device else False
        
        if command:
            # 如果配置中指定了命令，执行该命令
            if isinstance(command, dict):
                # 如果是字典，可能需要发送多个属性
                command = dict(command)
                for wire_key, attribute in self._config.get("include_attributes", {}).items():
                    value = self._get_nested_value(attribute)
                    if value is None:
                        raise HomeAssistantError("Select the required settings before starting")
                    command[wire_key] = value
                await self.async_set_attributes(command)
                zero_attributes = self._config.get("verify_zero_attributes", [])
                if zero_attributes and any(self._get_nested_value(key) != 0 for key in zero_attributes):
                    # This appliance sometimes needs a second stop to clear storage.
                    await self.async_set_attributes(command)
                    if any(self._get_nested_value(key) != 0 for key in zero_attributes):
                        raise HomeAssistantError("Device did not confirm that the operation stopped")
                positive_attribute = self._config.get("verify_positive_attribute")
                if positive_attribute and not self._get_nested_value(positive_attribute):
                    raise HomeAssistantError("Device did not confirm that the operation started")
            elif isinstance(command, str):
                # 如果是字符串，可能是特殊命令类型
                await self._async_execute_command(command)
        elif value is not None:
            # 如果配置中指定了值，设置该属性值
            await self.async_set_attribute(attribute, value)
        else:
            # 默认行为：如果没有指定命令或值，记录警告
            MideaLogger.warning(
                f"Button {self._entity_key} has no command or value configured"
            )

    async def _async_execute_command(self, command: str) -> None:
        """Execute a special command."""
        # 这里可以处理特殊的命令类型
        # 例如：重启、重置、测试等
        if command == "reset" or command == "restart":
            # 可以在这里实现重置或重启逻辑
            MideaLogger.debug(f"Executing {command} command for button {self._entity_key}")
        else:
            # 对于其他命令，可以通过 coordinator 发送
            await self.coordinator.async_send_command(0, command)

