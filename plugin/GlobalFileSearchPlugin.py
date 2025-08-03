import os
import fnmatch
from abstract_plugin import AbstractPlugin, PluginResult

class GlobalFileSearchPlugin(AbstractPlugin):
    def __init__(self):
        super().__init__()
        self.searching = False
        self.max_results = 20  # 最大返回结果数

    def valid(self) -> bool:
        return True  # 此插件总是可用

    def init(self, logger):
        self.logger = logger
        self.logger.info("GlobalFileSearchPlugin 初始化完成")

    def get_name(self) -> str:
        return "GlobalFileSearchPlugin"

    def search_files(self, pattern: str, start_path: str = "/"):
        """全局搜索文件"""
        if not pattern:
            return "请输入搜索关键词"
        
        self.searching = True
        results = []
        pattern = pattern.lower()
        
        for root, _, files in os.walk(start_path):
            if not self.searching:  # 检查是否已停止搜索
                break
                
            for file in files:
                if fnmatch.fnmatch(file.lower(), f"*{pattern}*"):
                    results.append(os.path.join(root, file))
                    if len(results) >= self.max_results:
                        self.searching = False
                        break
        
        self.searching = False
        
        if not results:
            return "未找到匹配的文件"
        
        result_str = f"找到 {len(results)} 个结果:\n"
        for i, path in enumerate(results[:self.max_results], 1):
            result_str += f"{i}. {path}\n"
        
        if len(results) > self.max_results:
            result_str += f"\n(仅显示前 {self.max_results} 个结果)"
        
        return result_str

    def run(self, command: str, args: dict) -> PluginResult:
        original_command = args.get('original_command', '')
        
        if "搜索文件" in original_command:
            pattern = original_command.replace("搜索文件", "").strip()
            if not pattern:
                return PluginResult(
                    success=False, 
                    error_message="请输入要搜索的文件名关键词"
                )
            
            # 在实际应用中，可能需要根据操作系统设置不同的起始路径
            start_path = "/" if os.name == 'posix' else "C:\\"
            
            try:
                result = self.search_files(pattern, start_path)
                return PluginResult(success=True, result=result)
            except Exception as e:
                return PluginResult(success=False, error_message=f"搜索失败: {str(e)}")
        
        return PluginResult(
            success=False,
            error_message="无法识别的搜索命令，请使用'搜索文件 [关键词]'"
        )

    def stop(self):
        self.searching = False
        return PluginResult(success=True, result="文件搜索已停止")

    def status(self):
        status = "正在搜索中" if self.searching else "空闲"
        return PluginResult(success=True, result=f"文件搜索插件状态: {status}")

    def cleanup(self):
        self.searching = False
