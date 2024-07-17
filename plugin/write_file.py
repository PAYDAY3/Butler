import logging
import os
import time

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand

TEMP_DIR_PATH = "./temp"

class WriteFilePlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "write_file"

    def get_chinese_name(self):
        return "写入文件"

    def get_description(self):
        return "写入文件内容接口，当你需要向一个文件中写入内容时，你应该调用本接口，传入要写入的内容。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "要写入的内容",
                },
            },
            "required": ["file_path", "content"],
        }

def run(self, takecommand: str, args: dict) -> PluginResult:
    if takecommand is None:
        return PluginResult.new("没有检测到语音指令", need_call_brain=False)

    content = args.get("content")
    if content:
        file_name = f"write_file-{str(int(time.time()))}.md"
        file_path = os.path.abspath(os.path.join(TEMP_DIR_PATH, file_name))
        with open(file_path, "w") as f:
            f.write(content)
        return PluginResult.new(result=f"已将内容写入到文件【{file_path}】中。", need_call_brain=True)
    else:
        return PluginResult.new(result="写入内容不能为空。", need_call_brain=False)
