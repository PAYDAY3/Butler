import os
import random
import time
from my_package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand, speak

logging = Logging.getLogger(__name__)

class JokePlugin(AbstractPlugin):
    def __init__(self):
        self.name = "JokePlugin"
        self.chinese_name = "笑话插件"
        self.description = "随机讲笑话并朗读"
        self.parameters = {}  # 此插件不需要参数
        self.jokes = [
            "为什么企鹅不会飞？因为他们太胖了！",
            "为什么树木总是在看地图？因为它们总是迷路！",
            "为什么蜗牛总是背着房子？因为它们太宅了！",
            "为什么小明总是喜欢玩游戏？因为游戏比学习有趣多了！",
            "为什么老师总是喜欢提问？因为他们想看看学生有没有认真听课！",
            "为什么猪总是喜欢睡觉？因为他们太懒了！",
            # ... 更多笑话
        ]

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
        self.logger.info("JokePlugin 开始.")

    def on_shutdown(self):
        self.logger.info("JokePlugin 关闭.")

    def on_pause(self):
        self.logger.info("JokePlugin 停顿了一下.")

    def on_resume(self):
        self.logger.info("JokePlugin 恢复.")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        if any(keyword in takecommand for keyword in ["我无聊了", "休息一下", "讲个笑话", "好无聊"]):
            # 随机选择一个笑话
            joke_question, joke_answer = random.choice(self.jokes)
            speak(joke_question)  # 调用你的 speak 函数
            time.sleep(3)  # 停顿3秒（可以根据需要调整）
            speak(joke_answer)  # 然后说出答案部分
            return PluginResult.new(result=joke, need_call_brain=False, success=True)
        else:
            return PluginResult.new(result=None, need_call_brain=False, success=False) 
