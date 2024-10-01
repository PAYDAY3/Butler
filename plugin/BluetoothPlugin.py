import os
import bluetooth
from package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult

logger = Logging.getLogger(__name__)

class BluetoothPlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def init(self, logger):
        self.name = "bluetooth"
        self.chinese_name = "蓝牙控制"
        self.description = "通过蓝牙控制设备的插件"
        self._logger = logger

    def get_name(self):
        return self.name

    def get_chinese_name(self):
        return self.chinese_name

    def get_description(self):
        return self.description

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "要执行的动作，如 '搜索设备', '连接设备', '发送命令'",
                },
                "device_address": {
                    "type": "string",
                    "description": "目标设备的蓝牙地址",
                },
                "command": {
                    "type": "string",
                    "description": "要发送的命令（适用于发送命令操作）",
                },
            },
            "required": ["action"],
        }

    def run(self, takecommand: str, args: dict) -> PluginResult:
        self._logger.info("开始执行蓝牙操作")
        
        action = args.get("action")
        device_address = args.get("device_address")
        command = args.get("command")

        if action == "搜索设备":
            return self.discover_devices()
        elif action == "连接设备":
            return self.connect_device(device_address)
        elif action == "发送命令":
            return self.send_command(device_address, command)
        else:
            self._logger.warning("无效的操作")
            return PluginResult.new("无效的操作", need_call_brain=False)

    def discover_devices(self) -> PluginResult:
        self._logger.info("正在搜索蓝牙设备...")
        devices = bluetooth.discover_devices(duration=8, lookup_names=True)

        if not devices:
            self._logger.warning("未找到任何蓝牙设备")
            return PluginResult.new("未找到任何蓝牙设备", need_call_brain=False)

        device_list = "\n".join([f"{name} ({addr})" for addr, name in devices])
        self._logger.info(f"找到以下蓝牙设备:\n{device_list}")
        return PluginResult.new(result=f"找到以下蓝牙设备:\n{device_list}", need_call_brain=True)

    def connect_device(self, device_address: str) -> PluginResult:
        self._logger.info(f"尝试连接设备: {device_address}")
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((device_address, 1))
            self._logger.info(f"成功连接到设备: {device_address}")
            return PluginResult.new(result=f"成功连接到设备: {device_address}", need_call_brain=True)
        except Exception as e:
            self._logger.error(f"连接失败: {str(e)}")
            return PluginResult.new(result=f"连接失败: {str(e)}", need_call_brain=False)

    def send_command(self, device_address: str, command: str) -> PluginResult:
        if not command:
            self._logger.warning("发送命令不能为空")
            return PluginResult.new("发送命令不能为空", need_call_brain=False)

        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((device_address, 1))
            sock.send(command.encode('utf-8'))
            sock.close()
            self._logger.info(f"已向设备 {device_address} 发送命令: {command}")
            return PluginResult.new(result=f"已向设备 {device_address} 发送命令: {command}", need_call_brain=True)
        except Exception as e:
            self._logger.error(f"发送命令时出错: {str(e)}")
            return PluginResult.new(result=f"发送命令时出错: {str(e)}", need_call_brain=False)
