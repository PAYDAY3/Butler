import importlib
import pkgutil
import inspect
from abc import ABC, abstractmethod
from typing import Type, Optional, List, Dict
from jarvis.jarvis import takecommand
from my_package import Logging

logger = Logging.getLogger(__name__)

class PluginManager:
    def __init__(self, plugin_package: str):
        self.plugin_package = plugin_package
        # self.plugins = {}
        self.plugins: Dict[str, AbstractPlugin] = {}
        self.logger = logging.getLogger("PluginManager")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.load_all_plugins()
        
    # 动态加载单个插件
    def load_plugin(self, module_name, class_name: str) -> Optional[AbstractPlugin]:
        try:
            module = importlib.import_module(module_name)
            # plugin_class = getattr(module, class_name)  
            plugin_class: Type[AbstractPlugin] = getattr(module, class_name)
            plugin_instance = plugin_class()
            if plugin_instance.valid():
                plugin_instance.init(self.logger)
                self.plugins[plugin_instance.get_name()] = plugin_instance
                self.logger.info(f"已加载插件: {plugin_instance.get_name()}")
                return plugin_instance
            else:
                self.logger.warning(f"插件 {plugin_instance.get_name()} 无效.")
                return None
        except (ModuleNotFoundError, AttributeError) as e:
            self.logger.error(f"加载插件 {module_name}.{class_name} 失败: {e}")
            return None

    # 获取插件
    def get_plugin(self, name: str) -> Optional[AbstractPlugin]:
        if name in self.plugins:
            return self.plugins[name]
        
        # 遍历插件包中的所有模块，按需加载插件
        for importer, module_name, ispkg in pkgutil.walk_packages([self.plugin_package]):
            if not ispkg:
                module = importlib.import_module(module_name)
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if inspect.isclass(attribute) and issubclass(attribute, AbstractPlugin) and not inspect.isabstract(attribute):
                        if attribute.__name__.endswith("Plugin"):
                            plugin_instance = self.load_plugin(module_name, attribute.__name__)
                            if plugin_instance and plugin_instance.get_name() == name:
                                return plugin_instance
        return None

    # 获取所有插件
    def get_all_plugins(self) -> List[AbstractPlugin]:
        # 遍历插件包中的所有模块，按需加载所有插件
        for importer, module_name, ispkg in pkgutil.walk_packages([self.plugin_package]):
            if not ispkg:
                module = importlib.import_module(module_name)
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if inspect.isclass(attribute) and issubclass(attribute, AbstractPlugin) and not inspect.isabstract(attribute):
                        if attribute.__name__.endswith("Plugin"):
                            self.load_plugin(module_name, attribute.__name__)
        return list(self.plugins.values())

    # 运行插件
    def run_plugin(self, name, takecommand: str, args: List[str]) -> Optional[str]:
        plugin = self.get_plugin(name)
        # plugin_name = takecommand.split()[0]  # 假设插件名称在命令的开头
        # plugin = self.plugins.get(plugin_name)
        if plugin:
            self.logger.info(f"正在运行插件: {name}")
            result = plugin.run(takecommand, args)
            self.logger.info(f"插件 {name} 运行结果: {result}")
            return result
        else:
            self.logger.error(f"未找到插件 {name}.")
            return None
    
    def stop_plugin(self, name: str) -> Optional[str]:
        plugin = self.get_plugin(name)
        if plugin:
            self.logger.info(f"正在停止插件: {name}")
            result = plugin.stop()
            self.logger.info(f"插件 {name} 停止结果: {result}")
            return result
        else:
            self.logger.error(f"未找到插件 {name}.")
            return None
    
    def get_plugin_status(self, name: str) -> Optional[str]:
        plugin = self.get_plugin(name)
        if plugin:
            self.logger.info(f"正在获取插件状态: {name}")
            result = plugin.status()
            self.logger.info(f"插件 {name} 状态: {result}")
            return result
        else:
            self.logger.error(f"未找到插件 {name}.")
            return None
