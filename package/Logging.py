import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from pathlib import Path

class Logger:
    _configured = False
    _loggers = {}
    
    @classmethod
    def _configure(cls, log_dir="logs", log_level=logging.INFO, 
                   max_bytes=5*1024*1024, backup_count=3):
        """
        配置日志系统（只执行一次）
        
        参数:
            log_dir: 日志目录路径
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: 日志文件最大字节数
            backup_count: 备份文件数量
        """
        if cls._configured:
            return
            
        # 创建日志目录（如果不存在）
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 基本配置
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器（所有级别）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 1. 总日志文件（所有级别）
        all_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, "all.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        all_handler.setFormatter(formatter)
        root_logger.addHandler(all_handler)
        
        # 2. INFO级别日志文件
        info_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, "info.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        info_handler.setFormatter(formatter)
        info_handler.setLevel(logging.INFO)
        info_handler.addFilter(lambda record: record.levelno == logging.INFO)
        root_logger.addHandler(info_handler)
        
        # 3. WARNING级别日志文件
        warning_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, "warning.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        warning_handler.setFormatter(formatter)
        warning_handler.setLevel(logging.WARNING)
        warning_handler.addFilter(lambda record: record.levelno == logging.WARNING)
        root_logger.addHandler(warning_handler)
        
        # 4. ERROR级别日志文件（包含ERROR和CRITICAL）
        error_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, "error.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)
        
        # 5. DEBUG级别日志文件（可选）
        debug_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, "debug.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG)
        root_logger.addHandler(debug_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name=None):
        """
        获取配置好的日志记录器
        
        参数:
            name: 日志记录器名称（通常使用 __name__）
            
        返回:
            配置好的 logging.Logger 实例
        """
        # 确保配置已执行
        if not cls._configured:
            cls._configure()
            
        # 获取或创建日志记录器
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        return cls._loggers[name]
    
    @classmethod
    def configure(cls, **kwargs):
        """
        自定义日志配置（必须在首次获取日志记录器前调用）
        
        参数:
            log_dir: 日志目录路径
            log_level: 日志级别
            max_bytes: 日志文件最大字节数
            backup_count: 备份文件数量
        """
        if not cls._configured:
            cls._configure(**kwargs)
        else:
            raise RuntimeError("Logger already configured. Configure must be called before first use.")
