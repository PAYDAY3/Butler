import os
import time
from my_package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand
logging = Logging.getLogger(_name_)

class FileSearchPlugin(AbstractPlugin):
    def __init__(self):
        self.name = "FileSearchPlugin"
        self.chinese_name = "文件搜索"
        self.description = "搜索指定目录中的文件"
        self.parameters = {"directory": "str", "filename": "str"}

    def valid(self) -> bool:
        return True

    def init(self, logging):
        self.logger = logging.getLogger(self.name)

    def get_name(self):
        return self.name

    def get_chinese_name(self):
        return self.chinese_name

    def get_description(self):
        return self.description

    def get_parameters(self):
        return self.parameters

    def on_startup(self):
        self.logger.info("文件搜索插件开始.")

    def on_shutdown(self):
        self.logger.info("文件搜索插件关闭.")

    def on_pause(self):
        self.logger.info("文件搜索插件停顿了一下.")

    def on_resume(self):
        self.logger.info("文件搜索插件恢复.")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        directory = args.get("directory")
        filename = args.get("filename")
        if not directory or not filename:
            return PluginResult.new(result=None, need_call_brain=False, success=False, error_message="directory或filename参数缺失")

        try:
            matches = []
            for root, _, files in os.walk(directory):
                if filename in files:
                    matches.append(os.path.join(root, filename))
            
            if matches:
                result = f"找到文件：{matches}"
                return PluginResult.new(result=result, need_call_brain=False, success=True)
            else:
                return PluginResult.new(result="未找到文件", need_call_brain=False, success=True)
        except Exception as e:
            return PluginResult.new(result=None, need_call_brain=False, success=False, error_message=str(e))
