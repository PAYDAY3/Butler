import tkinter as tk
from tkinter import messagebox
from package.log_manager import LogManager
from .PluginManager import PluginManager

# 配置日志
logger = LogManager.get_logger(__name__)

# 初始化 PluginManager 并传入插件包的路径
plugin_manager = PluginManager(plugin_package="plugin")

# 加载所有插件
all_plugins = plugin_manager.get_all_plugins()
logger.info(f"已加载插件: {[plugin.get_name() for plugin in all_plugins]}")

def match_command_to_plugin(command: str):
    """
    Matches a command to a plugin.
    """
    for plugin in plugin_manager.get_all_plugins():
        for cmd in plugin.get_commands():
            if plugin.get_match_type() == 'exact' and command.lower() == cmd.lower():
                return plugin.get_name(), {}, plugin
            elif plugin.get_match_type() == 'prefix' and command.lower().startswith(cmd.lower()):
                return plugin.get_name(), {}, plugin
            elif plugin.get_match_type() == 'contains' and cmd.lower() in command.lower():
                return plugin.get_name(), {}, plugin
    return None, None, None
    
def process_command(command: str):
    """处理指令并执行相应的插件."""
    plugin_name, args, plugin = match_command_to_plugin(command)

    if plugin_name:
        logger.info(f"匹配到插件: {plugin_name}，执行中...")
        result = plugin_manager.run_plugin(name=plugin_name, takecommand=command, args=args)
        logger.info(f"{plugin_name} 运行结果: {result}")
        
        status = plugin_manager.get_plugin_status(name=plugin_name)
        logger.info(f"{plugin_name} 状态: {status}")

        stop_result = plugin_manager.stop_plugin(name=plugin_name)
        logger.info(f"{plugin_name} 停止结果: {stop_result}")
        return f"{plugin_name} 运行结果: {result}, 状态: {status}, 停止结果: {stop_result}"
    else:
        return "未找到匹配的插件。请尝试其他命令。"
