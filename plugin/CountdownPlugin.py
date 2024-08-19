from datetime import datetime, timedelta
from my_package import Logging
from abc import ABCMeta, abstractmethod
from jarvis.jarvis import takecommand,speak
from datetime import datetime
from plugin.plugin_interface import AbstractPlugin, PluginResult

logging = Logging.getLogger(__name__)

class CountdownPlugin(AbstractPlugin):
    def __init__(self):
        self.name = "倒计时"
        self.chinese_name = ""
        self.description = ""
        self.parameters = {}

    def valid(self) -> bool:
        return True

    def init(self, logging):
        self.logging = Logging.getLogger(self.name)

    def get_name(self):
        return self.name

    def get_chinese_name(self):
        return self.chinese_name

    def get_description(self):
        return self.description

    def get_parameters(self):
        return self.parameters

    def on_startup(self):
        logging.info("倒计时插件开始")

    def on_shutdown(self):
        logging.info("倒计时插件停止")

    def on_pause(self):
        logging.info("倒计时插件停止")

    def on_resume(self):
        logging.info("倒计时插件恢复")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        if "运行" in takecommand:
            if "秒" in takecommand:
                seconds = int(takecommand.split("秒")[0].split("运行")[-1])
                end_time = datetime.now() + timedelta(seconds=seconds)
                while datetime.now() < end_time:
                    remaining_time = (end_time - datetime.now()).seconds
                    speak(f"剩余时间: {remaining_time} 秒")
                    time.sleep(1)
                logging.info("倒计时结束")
                return PluginResult.new("倒计时结束", False)
            else:
                return PluginResult.new("无效的参数", False, error_message="Missing '秒' argument")
        else:
            return PluginResult.new("无效的命令", False)
