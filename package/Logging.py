import logging
import os
from logging.handlers import RotatingFileHandler
import threading

PAGE = 4096

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR

TEMP_PATH = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.getenv("LOG_FILE", "logging.txt")

log_directory_lock = threading.Lock()

def ensure_log_directory():
    """确保日志目录存在，如果不存在则创建"""
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)

def tail(filepath, n=10):
    """高效实现 tail -n"""
    buffer_size = 8192
    with open(filepath, 'rb') as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        offset = min(file_size, buffer_size)
        lines = []
        while len(lines) <= n and offset < file_size:
            f.seek(-offset, os.SEEK_END)
            lines = f.readlines()
            offset += buffer_size
        return b''.join(lines[-n:]).decode('utf-8')

def getLogger(name):
    """自定义 getLogger 函数，确保线程安全"""
    with log_directory_lock:
        ensure_log_directory()
        format = "%(asctime)s - %(name)s - %(filename)s - %(funcName)s - line %(lineno)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format)
        logging.basicConfig(format=format)
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        log_file_path = os.path.join(TEMP_PATH, LOG_FILE)

        if not logger.handlers:
            try:
                file_handler = RotatingFileHandler(
                    log_file_path,
                    maxBytes=10 * 1024 * 1024,  # 10 MB
                    backupCount=5
                )
                file_handler.setLevel(logging.NOTSET)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except OSError as e:
                print(f"初始化日志处理器失败: {e}")

    return logger

def readLog(lines=200):
    """获取最新的指定行数的日志"""
    log_path = os.path.join(TEMP_PATH, LOG_FILE)
    try:
        if os.path.exists(log_path):
            return tail(log_path, lines)
    except OSError as e:
        print(f"读取日志时出错: {e}")
    return ""

def split_logs(log_file_name, output_files):
    """根据程序名称将日志分割到不同的文件中"""
    log_path = os.path.join(TEMP_PATH, LOG_FILE)

    if not os.path.exists(log_path):
        for file_path in output_files.values():
            if not os.path.exists(file_path):
                with open(file_path, "w"):
                    pass  # 创建空文件
        return

    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"读取日志文件失败: {e}")
        return

    logs = {name: [] for name in output_files.keys()}
    logs["default"] = []

    for line in lines:
        if " - " in line:
            program_name = line.split(" - ")[1]
            logs.setdefault(program_name, []).append(line)
        else:
            logs["default"].append(line)

    for program_name, log_lines in logs.items():
        file_path = output_files.get(program_name, os.path.join(TEMP_PATH, f"{program_name}.txt"))
        with open(file_path, "a") as f:
            f.writelines(log_lines)

    try:
        open(log_path, "w").close()  # 清空日志文件
    except OSError as e:
        print(f"清空日志文件失败: {e}")
