import nltk
import os
import time
from my_package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand
logging = Logging.getLogger(__name__)

class NLPPlugin(AbstractPlugin):

    def __init__(self):
        self.name = "NLPPlugin"
        self.chinese_name = "自然语言处理插件"
        self.description = "执行基本自然语言处理任务的插件。"
        self.parameters = {"text": "要处理的文本", "operation": "操作类型"}

    def valid(self) -> bool:
        return True

    def init(self, logging):
        self.logger = logging
        self.logger.info(f"{self.name} initialized.")
        nltk.download('punkt')

    def get_name(self):
        return self.name

    def get_chinese_name(self):
        return self.chinese_name

    def get_description(self):
        return self.description

    def get_parameters(self):
        return self.parameters

    def on_startup(self):
        self.logger.info(f"{self.name} started up.")

    def on_shutdown(self):
        self.logger.info(f"{self.name} shut down.")

    def on_pause(self):
        self.logger.info(f"{self.name} paused.")

    def on_resume(self):
        self.logger.info(f"{self.name} resumed.")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        text = args.get("text")
        operation = args.get("operation")
        
        try:
            if operation == "tokenize":
                result = nltk.word_tokenize(text)
            elif operation == "sentence_tokenize":
                result = nltk.sent_tokenize(text)
            else:
                result = "未知操作类型"
            success = True
        except Exception as e:
            result = str(e)
            success = False

        self.logger.info(f"Running {self.name} with command: {takecommand} and args: {args}")
        return PluginResult.new(result=result, need_call_brain=False, success=success)
