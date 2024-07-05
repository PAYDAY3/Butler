import json
import os
import time
from util import *
from PIL import Image
import shutil
import Logging
import speech_recognition as sr
from my_package.takecommand import takecommand

# 存档文件路径
archive_file = "archive.json"
file_path="/data" #文件夹位置
logging = Logging.getLogger(__name__)

# 创建存档
def create_archive(data):
    with open(archive_file, "w") as file:
        json.dump(data, file)

# 读取存档
def load_archive():
    try:
        with open(archive_file, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return None

# 更新存档
def update_archive(data):
    existing_data = load_archive()

    if existing_data is not None:
        existing_data.update(data)
        create_archive(existing_data)
    else:
        create_archive(data)

# 保存文本文件
def save_text_file(file_path, content):
    try:
        with open(file_path, "w") as file:
            file.write(content)
        print(f"已保存文本文件：{file_path}")
        logging.info(f"保存文本文件：{file_path}")
    except Exception as e:
        print(f"保存文本文件出错：{e}")
        logging.error(f"保存文本文件出错：{e}")

# 保存图片文件
def save_image_file(file_path, new_name):
    try:
        image = Image.open(file_path)
        image.save(new_name)
        print(f"已保存图片文件：{new_name}")
        logging.info(f"保存图片文件：{new_name}")
    except Exception as e:
        print(f"保存图片文件出错：{e}")
        logging.error(f"保存图片文件出错：{e}")

# 查找文件
def find_file(file_name):
    try:
        result = []
        for root, dirs, files in os.walk(".", topdown=True):
            for file in files:
                if file_name in file:
                    result.append(file)  # 只保存文件名而不是完整路径

        if result:
            print("找到以下文件：")
            for i, file_name in enumerate(result):
                print(i + 1, ":", file_name)
            logging.info(f"查找文件：{file_name}，找到 {len(result)} 个文件")
        else:
            print("未找到符合条件的文件。")
            logging.info(f"查找文件：{file_name}，未找到符合条件的文件")
    except Exception as e:
        print(f"查找文件出错：{e}")
        logging.error(f"查找文件出错：{e}")
        
# 打开图片文件
def open_image_file(file_path):
    try:
        image = Image.open(file_path)
        image.show()
        print(f"已打开图片文件：{file_path}")
        logging.info(f"打开图片文件：{file_path}")
    except Exception as e:
        print(f"打开图片文件出错：{e}")
        logging.error(f"打开图片文件出错：{e}")

# 打开文本文件
def open_text_file(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read()
            print(content)
        print(f"已打开文本文件：{file_path}")
        logging.info(f"打开文本文件：{file_path}")
    except Exception as e:
        print(f"打开文本文件出错：{e}")
        logging.error(f"打开文本文件出错：{e}")
        
# 删除文件
def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"已删除文件：{file_path}")
        logging.info(f"删除文件：{file_path}")
    except Exception as e:
        print(f"删除文件出错：{e}")
        logging.error(f"删除文件出错：{e}")
        
# 创建文件夹
def create_folder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"已创建文件夹：{folder_path}")
        logging.info(f"创建文件夹：{folder_path}")
    except Exception as e:
        print(f"创建文件夹出错：{e}")
        logging.error(f"创建文件夹出错：{e}")

# 删除文件夹
def delete_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"已删除文件夹：{folder_path}")
            logging.info(f"删除文件夹：{folder_path}")
        except Exception as e:
            print("删除文件夹出错：{e}")
            logging.error(f"删除文件夹出错：{e}")
    else:
        print("文件夹不存在。")

# 查看文件夹
def list_folder(folder_path):
    try:
        files = os.listdir(folder_path)
        if len(files) > 0:
            print(f"文件夹 {folder_path} 包含以下文件和子文件夹：")
            for i, file in enumerate(files):
                print(i+1, ":", file)
        logging.info(f"查看文件夹：{folder_path}，包含 {len(files)} 个文件/子文件夹")
        else:
            print(f"文件夹 {folder_path} 是空的。")
            logging.info(f"查看文件夹：{folder_path}，文件夹是空的")
    except Exception as e:
        print(f"列出文件夹内容出错：{e}")
        logging.error(f"列出文件夹内容出错：{e}")    
    except FileNotFoundError:
        print("文件夹不存在。")

# 重命名文件
def rename_file(file_path, new_name):
    try:
        os.rename(file_path, os.path.join(os.path.dirname(file_path), new_name))
        print(f"已将文件 {src_file} 重命名为 {new_name}")
        logging.info(f"重命名文件：{src_file} 为 {new_name}")
    except FileNotFoundError:
        print("文件不存在。")
    except FileExistsError:
        print("新文件名已存在。")
    except Exception as e:
        print(f"重命名文件出错：{e}")
        logging.error(f"重命名文件出错：{e}")

# 复制文件
def copy_file(src_file, dest_folder):
    try:
        shutil.copy(src_file, dest_folder)
        print(f"已将文件 {src_file} 复制到 {dest_folder}")
        logging.info(f"复制文件：{src_file} 到 {dest_folder}")
    except Exception as e:
        print(f"复制文件出错：{e}")
        logging.error(f"复制文件出错：{e}")
        
# 移动文件
def move_file(src_file, dest_folder):
    try:
        shutil.move(src_file, dest_folder)
        print(f"已将文件 {src_file} 移动到 {dest_folder}")
        logging.info(f"移动文件：{src_file} 到 {dest_folder}")
    except Exception as e:
        print(f"移动文件出错：{e}")
        logging.error(f"移动文件出错：{e}")

# 粘贴文件
def paste_file(src_file, dest_folder):
    try:
        shutil.copy(src_file, dest_folder)
        print(f"已粘贴文件 {src_file} 到 {dest_folder}")
        logging.info(f"粘贴文件：{src_file} 到 {dest_folder}")
    except Exception as e:
        print(f"粘贴文件出错：{e}")
        logging.error(f"粘贴文件出错：{e}")

# 处理命令
def process_command(takecommand):
    if "保存文件" in takecommand:
        filename = takecommand.split("保存文件")[-1].strip()
        content = input("请输入文本内容：")
        save_text_file(filename, content)
    elif "查找文件" in takecommand:
        filename = takecommand.split("查找文件")[-1].strip()
        find_file(filename)
    elif "删除文件" in takecommand:
        filename = takecommand.split("删除文件")[-1].strip()
        delete_file(filename)
    elif "打开图片" in takecommand:
        filename = takecommand.split("打开图片")[-1].strip()
        open_image_file(filename)
    elif "打开文件" in takecommand:
        filename = takecommand.split("打开文件")[-1].strip()
        open_text_file(filename)
    elif "创建文件夹" in takecommand:
        folder_path = takecommand.split("创建文件夹")[-1].strip()
        create_folder(folder_path)
    elif "删除文件夹" in takecommand:
        folder_path = takecommand.split("删除文件夹")[-1].strip()
        delete_folder(folder_path)
    elif "查看文件夹" in takecommand:
        folder_path = takecommand.split("查看文件夹")[-1].strip()
        list_folder(folder_path)
    elif "重命名文件" in takecommand:
        parts = takecommand.split("重命名文件")
        if len(parts) < 3:
            print("请提供文件路径和新的文件名。")
            logging.warning("重命名文件失败：未提供文件路径或新文件名")
        else:
            src_file, dest_folder = map(str.strip, file_path)
            move_file(src_file, dest_folder)
    elif "复制文件" in takecommand:
        parts = takecommand.split("复制文件")
        if len(parts) < 2:
            print("请提供源文件路径和目标文件夹路径")
            logging.warning("复制文件失败：未提供源文件路径或目标文件夹路径")
        else:
            src_file, dest_folder = map(str.strip, parts[1].split("到"))
            copy_file(src_file, dest_folder)
    elif "移动文件" in takecommand:
        parts = takecommand.split("移动文件")
        if len(parts) < 2:
            print("请提供源文件路径和目标文件夹路径")
            logging.warning("移动文件失败：未提供源文件路径或目标文件夹路径")
        else:
            src_file, dest_folder = map(str.strip, parts[1].split("到"))
            move_file(src_file, dest_folder)
    elif "粘贴文件" in takecommand:
        parts = takecommand.split("粘贴文件")
        if len(parts) < 2:
            print("请提供源文件路径和目标文件夹路径")
            logging.warning("粘贴文件失败：未提供源文件路径或目标文件夹路径")
        else:
            src_file, dest_folder = map(str.strip, parts[1].split("到"))
            paste_file(src_file, dest_folder)

    elif "退出" in takecommand:
        logging.info("退出程序")
        return False
    return True

# 主程序
def TextEditor():
    max_retries = 1  # 最大重试次数
    retries = 0

    while True:
        try:
            command = takecommand()
            if not command:
                continue
            if process_command(command):
                print("命令处理成功，程序继续执行。")
            else:
                print("命令处理失败，正在进行一次重试...")
                time.sleep(1)  # 等待一段时间后重试
        except Exception as e:
            print("发生错误：", e)
            if retries < max_retries:
                retries += 1
                print(f"已重试 {retries} 次。")
            else:
                print("重试次数已达上限，等待下一次错误再重试。")
                retries = 0
                time.sleep(5)  # 等待一段时间后继续

    if retries > max_retries:
        print("重试次数已达上限，程序退出。")
