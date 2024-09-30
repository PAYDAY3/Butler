import os
import shutil
import datetime
import logging
from package import Logging
from pathlib import Path
from typing import Optional

logging = Logging.getLogger(__name__)

def delete_temp_files(directory="./temp", log_file: Optional[str] = None, days: int = 7, backup_directory: Optional[str] = None, dry_run: bool = False):
    global last_execution_time

    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在")
        logging.info(f"目录 {directory} 不存在")
        return

    # 获取当前时间
    now = datetime.datetime.now()
    report = []

    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.access(file_path, os.R_OK):
                logger.warning(f"跳过不可读文件: {file_path}")
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
                logger.warning(f"Skipping unreadable directory: {dir_path}")
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

    # 记录当前执行时间
    last_execution_time = now
    print(f"上次执行时间: {last_execution_time}")
    logging.info(f"上次执行时间: {last_execution_time}")
    