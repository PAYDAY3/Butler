import os
import shutil
import datetime
import logging
from pathlib import Path
from typing import Optional
from package.log_manager import LogManager

logging = LogManager.get_logger(__name__)

def delete_temp_files(
    directory: str = "./temp",
    log_file: Optional[str] = None,
    days: int = 7,
    backup_directory: Optional[str] = None,
    dry_run: bool = False
) -> None:
    """
    删除指定目录下超过指定天数的临时文件和目录。

    Args:
        directory (str): 要清理的目录路径。
        log_file (Optional[str]): 日志文件路径。
        days (int): 超过该天数的文件和目录将被删除。
        backup_directory (Optional[str]): 备份目录路径。
        dry_run (bool): 如果为 True，则不实际删除文件和目录，只打印将要删除的内容。
    """
    global last_execution_time

    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在")
        logging.info(f"目录 {directory} 不存在")
        return

    now = datetime.datetime.now()
    report = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.access(file_path, os.R_OK):
                logging.warning(f"跳过不可读文件: {file_path}")
                continue

            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            file_age = (now - file_mtime).days

            if file_age > days:
                if backup_directory and os.path.exists(backup_directory):
                    backup_path = os.path.join(backup_directory, os.path.relpath(file_path, directory))
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    shutil.copy2(file_path, backup_path)
                    logging.info(f"备份文件: {file_path}到{backup_path}")

                if not dry_run:
                    try:
                        os.remove(file_path)
                        print(f"删除文件: {file_path}")
                        logging.info(f"删除文件: {file_path}")
                    except Exception as e:
                        print(f"删除文件 {file_path} 失败: {e}")
                        logging.error(f"删除文件 {file_path} 失败: {e}")

        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.access(dir_path, os.R_OK):
                logging.warning(f"跳过不可读目录: {dir_path}")
                continue

            dir_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(dir_path))
            dir_age = (now - dir_mtime).days

            if dir_age > days:
                if backup_directory and os.path.exists(backup_directory):
                    backup_path = os.path.join(backup_directory, os.path.relpath(dir_path, directory))
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    shutil.copytree(dir_path, backup_path)
                    logging.info(f"备份目录: {dir_path}到{backup_path}")

                if not dry_run:
                    try:
                        shutil.rmtree(dir_path)
                        print(f"删除目录: {dir_path}")
                        logging.info(f"删除目录: {dir_path}")
                        report.append(f"删除目录: {dir_path}")
                    except Exception as e:
                        print(f"删除目录 {dir_path} 失败: {e}")
                        logging.error(f"删除目录 {dir_path} 失败: {e}")

    print("“temp”目录下的符合条件的文件和目录已被删除")
    logging.info("“temp”目录下的符合条件的文件和目录已被删除")
    if report:
        with open('delete_report.txt', 'w') as f:
            for entry in report:
                f.write(f"{entry}\n")

    last_execution_time = now
    print(f"上次执行时间: {last_execution_time}")
    logging.info(f"上次执行时间: {last_execution_time}")
