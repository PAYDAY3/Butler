import os
import urllib.parse
from package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand, speak

logging = Logging.getLogger(__name__)

class SearchPlugin(AbstractPlugin):
    def __init__(self):
        self.name = "SearchPlugin"
        self.chinese_name = "搜索插件"
        self.description = "使用搜索引擎和视频网站搜索相关信息"
        self.parameters = {}  # 此插件不需要参数

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
        self.logger.info("SearchPlugin 开始.")

    def on_shutdown(self):
        self.logger.info("SearchPlugin 关闭.")

    def on_pause(self):
        self.logger.info("SearchPlugin 停顿了一下.")

    def on_resume(self):
        self.logger.info("SearchPlugin 恢复.")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        if "搜索" in takecommand:
            query = takecommand.replace("搜索", "").strip()
            if "bilibili" in takecommand:
                url = f"https://search.bilibili.com/all?keyword={urllib.parse.quote(query)}"
            elif "快手" in takecommand:
                url = f"https://www.kuaishou.com/search?q={urllib.parse.quote(query)}"
            elif "抖音" in takecommand:
                url = f"https://www.douyin.com/search/{urllib.parse.quote(query)}"
            elif "bing" in takecommand:
                url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
            elif "百度" in takecommand:
                url = f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}"
            else:
                return PluginResult.new(result=None, need_call_brain=False, success=False)

            speak(f"正在搜索 {query}。")
            return PluginResult.new(result=url, need_call_brain=False, success=True)
        else:
            return PluginResult.new(result=None, need_call_brain=False, success=False)
