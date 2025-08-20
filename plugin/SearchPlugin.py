import urllib.parse
from package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult

class SearchPlugin(AbstractPlugin):
    def __init__(self):
        self.name = "SearchPlugin"
        self.chinese_name = "搜索插件"
        self.description = "使用搜索引擎和视频网站搜索相关信息"
        self.parameters = {}  # 此插件不需要参数
        self.logger = Logging.get_logger(self.name)

    def valid(self) -> bool:
        return True

    def init(self, logging):
        self.logger = logging.get_logger(self.name)

    def get_name(self) -> str:
        return self.name

    def get_chinese_name(self) -> str:
        return self.chinese_name

    def get_description(self) -> str:
        return self.description

    def get_parameters(self) -> dict:
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
        if "搜索" not in takecommand:
            return PluginResult.new(result=None, need_call_brain=False, success=False)

        query = takecommand.replace("搜索", "").strip()
        search_engines = {
            "bilibili": f"https://search.bilibili.com/all?keyword={urllib.parse.quote(query)}",
            "快手": f"https://www.kuaishou.com/search?q={urllib.parse.quote(query)}",
            "抖音": f"https://www.douyin.com/search/{urllib.parse.quote(query)}",
            "bing": f"https://www.bing.com/search?q={urllib.parse.quote(query)}",
            "百度": f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}"
        }

        for key, url in search_engines.items():
            if key in takecommand:
                self.logger.info(f"正在使用 {key} 搜索 {query}.")
                speak(f"正在搜索 {query}。")
                return PluginResult.new(result=url, need_call_brain=False, success=True)

        self.logger.warning(f"未识别的搜索命令: {takecommand}")
        return PluginResult.new(result=None, need_call_brain=False, success=False)
