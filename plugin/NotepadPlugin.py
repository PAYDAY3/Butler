import os
import time
from my_package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand
logging = Logging.getLogger(__name__)

class NotepadPlugin(AbstractPlugin):
    def __init__(self):
        self.name = "NotepadPlugin"
        self.chinese_name = "记事本"
        self.description = "记录简单的文本笔记"
        self.parameters = {"note": "str"}
        self.notes = []

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
        self.logger.info("NotepadPlugin started.")

    def on_shutdown(self):
        self.logger.info("NotepadPlugin shutdown.")

    def on_pause(self):
        self.logger.info("NotepadPlugin paused.")

    def on_resume(self):
        self.logger.info("NotepadPlugin resumed.")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        note = args.get("note")
        if not note:
            return PluginResult.new(result=None, need_call_brain=False, success=False, error_message="Note parameter is missing")
        
        self.notes.append(note)
        result = "Note added successfully"
        return PluginResult.new(result=result, need_call_brain=False, success=True)
