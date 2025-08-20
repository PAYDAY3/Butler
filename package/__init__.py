from .log_manager import LogManager

# 提供模块级别的快捷访问
getLogger = LogManager.get_logger
