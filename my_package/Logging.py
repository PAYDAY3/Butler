import logging
import os
from logging.handlers import RotatingFileHandler

PAGE = 4096

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR

TEMP_PATH = "logs"  # 存储日志文件的目录
LOG_FILE = "logging.txt"  # 统一的日志文件名

def ensure_log_directory():
    """确保日志目录存在，如果不存在则创建"""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def tail(filepath, n=10):
    """
    实现 tail -n
    """
    res = ""
    with open(filepath, "rb") as f:
        f_len = f.seek(0, 2)
        rem = f_len % PAGE
        page_n = f_len // PAGE
        r_len = rem if rem else PAGE
        while True:
            # 如果读取的页大小>=文件大小，直接读取数据输出
            if r_len >= f_len:
                f.seek(0)
                lines = f.readlines()[::-1]
                break

            f.seek(-r_len, 2)
            lines = f.readlines()[::-1]
            count = len(lines) - 1  # 末行可能不完整，减一行，加大读取量

            if count >= n:  # 如果读取到的行数>=指定行数，则退出循环读取数据
                break
            else:  # 如果读取行数不够，载入更多的页大小读取数据
                r_len += PAGE
                page_n -= 1

    for line in lines[:n][::-1]:
        res += line.decode("utf-8")
    return res

def getLogger(name):
    """
    作用同标准模块 logging.getLogger(name)
    """
    format = "%(asctime)s - %(name)s - %(filename)s - %(funcName)s - line %(lineno)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format)
    logging.basicConfig(format=format)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    log_file_path = os.path.join(TEMP_DIR, LOG_FILE)

    # 文件处理器，支持日志文件滚动
    if not logger.handlers:
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.NOTSET)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
                            
    return logger

def readLog(lines=200):
    """
    获取最新的指定行数的 log
    """
    log_path = os.path.join(TEMP_PATH)
    if os.path.exists(log_path):
        return tail(log_path, lines)
    return ""

def split_logs(log_file_name, output_files):
    """
    自动从 logging.txt 中获取日志，并根据程序名称将日志分割到不同的文件中
    """
    log_path = os.path.join(TEMP_DIR, LOG_FILE)

    if not os.path.exists(log_path):
        # 如果日志文件不存在，则不进行分割
        for file_path in output_files.values():
             if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    pass  # 创建空文件
        return
    
    with open(log_path, "r") as f:
        lines = f.readlines()

    logs = {name: [] for name in output_files.keys()}  # 用于存储不同程序的日志

    for line in lines:
        if " - " in line:
            program_name = line.split(" - ")[1]  # 提取程序名（即 logger 名）
            if program_name not in logs:
                logs[program_name] = []
            logs[program_name].append(line)

    # 将日志写入各自的文件中
    for program_name, log_lines in logs.items():
        log_file_name = f"{program_name}.txt"
        log_file_path = os.path.join(TEMP_DIR, log_file_name)
        with open(log_file_path, "a") as f:
            f.writelines(log_lines)

    # 写入到对应的文件中，如果文件不存在则创建
    for name, file_path in output_files.items():
        with open(file_path, "a") as f:  # 使用 "a" 模式追加内容
            f.write("\n".join(logs[name]) + "\n")

    # 清空 logging.txt 文件
    open(log_path, "w").close()
