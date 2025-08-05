"""工具集合管理类"""

from typing import Any

from deepseek.types.beta import BetaToolUnionParam  # DeepSeek API类型

from .base import BaseDeepSeekTool, ToolError, ToolFailure, ToolResult

class ToolCollection:
    """DeepSeek工具集合管理类"""
    
    def __init__(self, *tools: BaseDeepSeekTool):
        """初始化工具集合
        
        参数:
            *tools: 可变数量的工具实例
        """
        self.tools = tools
        # 创建工具名称到工具对象的映射
        self.tool_map = {tool.to_params()["name"]: tool for tool in tools}
    
    def to_params(self) -> list[BetaToolUnionParam]:
        """转换为DeepSeek API参数格式"""
        return [tool.to_params() for tool in self.tools]
    
    async def run(self, *, name: str, tool_input: dict[str, Any]) -> ToolResult:
        """执行指定工具
        
        参数:
            name: 工具名称
            tool_input: 工具输入参数
        返回:
            工具执行结果
        """
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"无效工具: {name}")
        
        try:
            # 执行工具并返回结果
            return await tool(**tool_input)
        except ToolError as e:
            # 捕获工具错误
            return ToolFailure(error=e.message)
