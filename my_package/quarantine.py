import os
import shutil
from my_package import Logging

# 设置日志记录
logging = Logging.getLogger(__name__)

def load_file_list(file_list_path):
    """加载文件名列表"""
    if not os.path.exists(file_list_path):
        return set()
    with open(file_list_path, 'r') as f:
        return set(line.strip() for line in f)

def save_file_list(file_list_path, file_list):
    """保存文件名列表"""
    with open(file_list_path, 'w') as f:
        for file_name in file_list:
            f.write(f"{file_name}\n")

def isolate_files(source_dir, quarantine_dir, file_list):
    """隔离未在文件列表中的文件"""
    if not os.path.exists(quarantine_dir):
        os.makedirs(quarantine_dir)
    for file_name in os.listdir(source_dir):
        file_path = os.path.join(source_dir, file_name)
        if os.path.isfile(file_path) and file_name not in file_list:
            quarantine_path = os.path.join(quarantine_dir, file_name)
            shutil.move(file_path, quarantine_path)
            logging.info(f"Moved: {file_path} to {quarantine_path}")
            print(f"Moved: {file_path} to {quarantine_path}")

def perform_security_check(file_path):
    """模拟安全检查"""
    logging.info(f"Performing security check on: {file_path}")
    return True  # 模拟检查通过

def release_files(quarantine_dir, source_dir, file_list):
    """检查并释放隔离区中的文件"""
    for file_name in os.listdir(quarantine_dir):
        file_path = os.path.join(quarantine_dir, file_name)
        if os.path.isfile(file_path) and perform_security_check(file_path):
            source_path = os.path.join(source_dir, file_name)
            shutil.move(file_path, source_path)
            file_list.add(file_name)
            logging.info(f"Released: {file_path} to {source_path}")
            print(f"Released: {file_path} to {source_path}")

def apply_file_permissions(file_path):
    """根据文件类型应用不同的权限策略"""
    if file_path.endswith('.sh') or file_path.endswith('.exe'):
        os.chmod(file_path, 0o700)  # 可执行文件，所有者可读写执行
    elif file_path.endswith('.txt') or file_path.endswith('.md'):
        os.chmod(file_path, 0o600)  # 文档文件，所有者可读写
    else:
        os.chmod(file_path, 0o644)  # 其他文件，所有者可读写，其他人只读

if __name__ == "__main__":
    source_directory = "safe_files"  # 替换为你的源目录
    quarantine_directory = "quarantine"  # 隔离目录
    file_list_path = "file_list.txt"  # 记录文件名的列表路径

    # 加载文件名列表
    file_list = load_file_list(file_list_path)

    # 隔离文件
    isolate_files(source_directory, quarantine_directory, file_list)

    # 禁用隔离区文件的执行权限
    for root, dirs, files in os.walk(quarantine_directory):
        for file in files:
            file_path = os.path.join(root, file)
            os.chmod(file_path, 0o600)  # 禁用执行权限
            # 需要特定的网络禁用实现，例如iptables等，这里省略

    # 检查并释放文件
    release_files(quarantine_directory, source_directory, file_list)

    # 为隔离区中的文件应用权限策略
    for root, dirs, files in os.walk(quarantine_directory):
        for file in files:
            apply_file_permissions(os.path.join(root, file))

    # 保存文件名列表
    save_file_list(file_list_path, file_list)
    
