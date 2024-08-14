import os
import time
from my_package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand
logging = Logging.getLogger(_name_)

class TimePlugin(AbstractPlugin):
    def __init__(self):
        self.name = "TimePlugin"
        self.chinese_name = "时间查询"
        self.description = "查询当前时间"
        self.parameters = {}

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
        self.logger.info("TimePlugin started.")

    def on_shutdown(self):
        self.logger.info("TimePlugin shutdown.")

    def on_pause(self):
        self.logger.info("TimePlugin paused.")

    def on_resume(self):
        self.logger.info("TimePlugin resumed.")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = f"Current time is {current_time}"
        return PluginResult.new(result=result, need_call_brain=False, success=True)
