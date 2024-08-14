import os
import time
from my_package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand
logging = Logging.getLogger(__name__)

class TodoPlugin(AbstractPlugin):
    def __init__(self):
        self.name = "TodoPlugin"
        self.chinese_name = "待办事项"
        self.description = "管理简单的待办事项列表"
        self.parameters = {"action": "str", "task": "str"}
        self.todo_list = []

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
        self.logger.info("TodoPlugin 开始.")

    def on_shutdown(self):
        self.logger.info("TodoPlugin 关闭.")

    def on_pause(self):
        self.logger.info("TodoPlugin 停顿了一下.")

    def on_resume(self):
        self.logger.info("TodoPlugin 恢复.")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        action = args.get("action")
        task = args.get("task")
        
        if not action:
            return PluginResult.new(result=None, need_call_brain=False, success=False, error_message="Action parameter is missing")
        
        if action == "add":
            if not task:
                return PluginResult.new(result=None, need_call_brain=False, success=False, error_message="Task parameter is missing")
            self.todo_list.append(task)
            result = f"任务 '{task}' 添加到待办事项列表"
        elif action == "list":
            result = "Todo list:\n" + "\n".join(self.todo_list)
        elif action == "remove":
            if not task:
                return PluginResult.new(result=None, need_call_brain=False, success=False, error_message="Task parameter is missing")
            if task in self.todo_list:
                self.todo_list.remove(task)
                result = f"任务 '{task}' 从待办事项列表中删除"
            else:
                result = f"任务 '{task}' 未在待办事项列表中找到"
        else:
            return PluginResult.new(result=None, need_call_brain=False, success=False, error_message="Invalid action")

        return PluginResult.new(result=result, need_call_brain=False, success=True)

