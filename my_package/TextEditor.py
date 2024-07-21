import json
import os
import time
import shutil
import logging
from PIL import Image
import speech_recognition as sr
from jarvis.jarvis import takecommand

# 配置
archive_file = "archive.json"
file_path = "/data"  # 主文件路径
temp_folder = "temp"  # 临时文件夹
logger = logging.getLogger(__name__)

# 存档管理
def create_archive(data):
    """创建新的存档文件并写入数据。"""
    with open(archive_file, "w") as file:
        json.dump(data, file)

def load_archive():
    """加载存档文件中的数据。"""
    try:
        with open(archive_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

def update_archive(data):
    """更新存档文件中的数据。"""
    existing_data = load_archive()
    if existing_data is not None:
        existing_data.update(data)
        create_archive(existing_data)
    else:
        create_archive(data)

# 文件操作
def save_text_file(file_path, content):
    """保存文本内容到指定路径的文件。"""
    try:
        with open(file_path, "w") as file:
            file.write(content)
        logger.info(f"保存文本文件：{file_path}")
    except Exception as e:
        logger.error(f"保存文本文件出错：{e}")

def save_image_file(file_path, new_name):
    """保存图像文件并重命名。"""
    try:
        image = Image.open(file_path)
        image.save(new_name)
        logger.info(f"保存图片文件：{new_name}")
    except Exception as e:
        logger.error(f"保存 {new_name} 图片文件出错：{e}")

def find_file(file_name):
    """查找匹配给定文件名的文件。"""
    try:
        result = []
        for root, dirs, files in os.walk("/", topdown=True):
            for file in files:
                if file_name in file:
                    result.append(os.path.join(root, file))

        if result:
            logger.info(f"找到 {len(result)} 个匹配的文件：{file_name}")
            return result
        else:
            logger.info(f"未找到匹配的文件：{file_name}")
            return []
    except Exception as e:
        logger.error(f"查找文件出错：{e}")
        return []

def open_image_file(file_path):
    """打开并显示图像文件。"""
    try:
        image = Image.open(file_path)
        image.show()
        logger.info(f"打开图片文件：{file_path}")
    except Exception as e:
        logger.error(f"打开 {file_path} 图片文件出错：{e}")

def open_text_file(file_path):
    """打开并读取文本文件。"""
    try:
        with open(file_path, "r") as file:
            content = file.read()
            print(content)
        logger.info(f"打开文本文件：{file_path}")
    except Exception as e:
        logger.error(f"打开 {file_path} 文本文件出错：{e}")

def delete_file(file_path):
    """删除指定路径的文件。"""
    try:
        os.remove(file_path)
        logger.info(f"删除文件：{file_path}")
    except Exception as e:
        logger.error(f"删除 {file_path} 文件出错：{e}")

def create_folder(folder_path):
    """创建新的文件夹。"""
    try:
        os.makedirs(folder_path, exist_ok=True)
        logger.info(f"创建文件夹：{folder_path}")
    except Exception as e:
        logger.error(f"创建 {folder_path} 文件夹出错：{e}")

def delete_folder(folder_path):
    """删除指定路径的文件夹。"""
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            logger.info(f"删除文件夹：{folder_path}")
        except Exception as e:
            logger.error(f"删除 {folder_path} 文件夹出错：{e}")
    else:
        logger.warning("文件夹不存在。")

def list_folder(folder_path):
    """列出文件夹中的内容。"""
    try:
        files = os.listdir(folder_path)
        if files:
            logger.info(f"文件夹 {folder_path} 包含 {len(files)} 个项目。")
            return files
        else:
            logger.info(f"文件夹 {folder_path} 是空的。")
            return []
    except Exception as e:
        logger.error(f"列出文件夹内容出错：{e}")
        return []

def rename_file(file_path, new_name):
    """重命名指定路径的文件。"""
    try:
        os.rename(file_path, os.path.join(os.path.dirname(file_path), new_name))
        logger.info(f"重命名文件为：{new_name}")
    except FileNotFoundError:
        logger.error("{new_name} 文件不存在。")
    except FileExistsError:
        logger.error("新 {new_name} 文件名已存在。")
    except Exception as e:
        logger.error(f"重命名文件出错：{e}")

def copy_file(src_file, dest_folder):
    """复制文件到目标文件夹。"""
    try:
        shutil.copy(src_file, dest_folder)
        logger.info(f"复制文件 {src_file} 到 {dest_folder}")
    except Exception as e:
        logger.error(f"复制文件 {src_file} 到 {dest_folder}：{e}")

def move_file(src_file, dest_folder):
    """移动文件到目标文件夹。"""
    try:
        shutil.move(src_file, dest_folder)
        logger.info(f"移动文件 {src_file} 到 {dest_folder}")
    except Exception as e:
        logger.error(f"移动文件 {src_file} 到 {dest_folder}：{e}")

def paste_file(src_file, dest_folder):
    """粘贴文件到目标文件夹。"""
    try:
        shutil.copy(src_file, dest_folder)
        logger.info(f"粘贴文件 {src_file} 到 {dest_folder}")
    except Exception as e:
        logger.error(f"粘贴文件 {src_file} 到 {dest_folder}：{e}")

# 命令处理
def process_command(command):
    """处理收到的命令。"""
    if "保存文件" in command:
        filename = command.split("保存文件")[-1].strip()
        content = input("请输入文本内容：")
        save_text_file(filename, content)
    elif "查找文件" in command:
        filename = command.split("查找文件")[-1].strip()
        find_file(filename)
    elif "删除文件" in command:
        filename = command.split("删除文件")[-1].strip()
        delete_file(filename)
    elif "打开图片" in command:
        filename = command.split("打开图片")[-1].strip()
        open_image_file(filename)
    elif "打开文件" in command:
        filename = command.split("打开文件")[-1].strip()
        open_text_file(filename)
    elif "创建文件夹" in command:
        folder_path = command.split("创建文件夹")[-1].strip()
        create_folder(folder_path)
    elif "删除文件夹" in command:
        folder_path = command.split("删除文件夹")[-1].strip()
        delete_folder(folder_path)
    elif "查看文件夹" in command:
        folder_path = command.split("查看文件夹")[-1].strip()
        list_folder(folder_path)
    elif "重命名文件" in command:
        parts = command.split("重命名文件")
        if len(parts) < 2:
            logger.warning("请提供文件路径和新的文件名。")
        else:
            src_file, new_name = map(str.strip, parts[1].split("为"))
            rename_file(src_file, new_name)
    elif "复制文件" in command:
        parts = command.split("复制文件")
        if len(parts) < 2:
            logger.warning("请提供源文件路径和目标文件夹路径。")
        else:
            src_file, dest_folder = map(str.strip, parts[1].split("到"))
            copy_file(src_file, dest_folder)
    elif "移动文件" in command:
        parts = command.split("移动文件")
        if len(parts) < 2:
            logger.warning("请提供源文件路径和目标文件夹路径。")
        else:
            src_file, dest_folder = map(str.strip, parts[1].split("到"))
            move_file(src_file, dest_folder)
    elif "粘贴文件" in command:
        parts = command.split("粘贴文件")
        if len(parts) < 2:
            logger.warning("请提供源文件路径和目标文件夹路径。")
        else:
            src_file, dest_folder = map(str.strip, parts[1].split("到"))
            paste_file(src_file, dest_folder)
    elif "退出" in command:
        logger.info("退出程序。")
        return False
    return True

def move_temp_files(temp_folder, target_folder):
    """将临时文件移动到目标文件夹。"""
    if os.path.exists(temp_folder):
        for filename in os.listdir(temp_folder):
            src_path = os.path.join(temp_folder, filename)
            dest_path = os.path.join(target_folder, filename)
            if os.path.isfile(src_path):
                try:
                    shutil.move(src_path, dest_path)
                    logger.info(f"移动临时文件 {filename} 到 {target_folder}")
                except Exception as e:
                    logger.error(f"移动临时文件出错：{e}")

def TextEditor():
    """主文本编辑器循环。"""
    max_retries = 1
    retries = 0

    while True:
        try:
            command = takecommand()
            if not command:
                continue
            if process_command(command):
                logger.info("命令处理成功，程序继续执行。")
            else:
                logger.warning("命令处理失败，正在重试...")
                time.sleep(1)
        except Exception as e:
            logger.error(f"发生错误：{e}")
            retries += 1
            if retries >= max_retries:
                logger.error("重试次数已达上限，退出程序。")
                break
            time.sleep(1)

    move_temp_files(temp_folder, file_path)

if __name__ == "__main__":
    TextEditor()
