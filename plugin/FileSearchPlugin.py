import os
import time
from my_package import Logging
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand,speak

logging = Logging.getLogger(_name_)

class FileSearchPlugin(AbstractPlugin):
    def __init__(self):
        self.name = "FileSearchPlugin"
        self.chinese_name = "文件搜索"
        self.description = "搜索指定目录中的文件"
        self.parameters = {
            "directory": "str", 
            "filename": "str",
            "foldername": "str",
            "目标文件夹": "str"
        }

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
        foldername = args.get("foldername")
        
        if not directory and not filename:
            return PluginResult.new(result=None, need_call_brain=False, success=False, error_message="directory或foldername和filename参数缺失")

        try:
            matches = []
            search_dir = directory if directory else '/'
            start_time = time.time()
            
            for root, dirs, files in os.walk(search_dir):
                if foldername and foldername in root.split(os.sep):
                    if filename in files:
                        matches.append(os.path.join(root, filename))
                elif not foldername and filename in files:
                    matches.append(os.path.join(root, filename))
                
                if time.time() - start_time > 10:  # 10 seconds timeout
                    break
            if matches:
                result = f"在 '{directory or foldername}' 找到文件：{', '.join(matches)}" 
                
                speak(f"找到文件 {filename}，是否要将其转移到指定文件夹？")
                user_response = takecommand().lower()
                
                if "yes" in user_response or "是" in user_response:
                    destination_directory = args.get("目标文件夹")
                    if not destination_directory:
                        return PluginResult.new(result=None, need_call_brain=False, success=False, error_message="目标文件夹参数缺失")
                    
                    for match in matches:
                        try:
                            os.rename(match, os.path.join(destination_directory, filename))
                            self.logger.info(f"文件 {filename} 已转移到 {destination_directory}")
                        except Exception as e:
                            self.logger.error(f"文件转移失败: {str(e)}")
                            return PluginResult.new(result=None, need_call_brain=False, success=False, error_message=f"文件转移失败: {str(e)}")
                    return PluginResult.new(result=result, need_call_brain=False, success=True)
            else:
                return PluginResult.new(result="未找到文件", need_call_brain=False, success=False)

        except Exception as e: 
            self.logger.error(f"文件搜索失败: {str(e)}")
            return PluginResult.new(result=None, need_call_brain=False, success=False, error_message=f"文件搜索失败: {str(e)}")                             
