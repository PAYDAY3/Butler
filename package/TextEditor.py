import json
import os
import time
import shutil
from package.log_manager import LogManager
from PIL import Image
import zipfile

# 配置
archive_file = "archive.json"
file_path = "/data"  # 主文件路径
temp_folder = "temp"  # 临时文件夹
logger = Logging.get_logger(__name__)

class Zip:
    # 创建压缩文件方法，可指定文件路径、压缩文件路径、密码
    @staticmethod
    def create_zip(file_path, zip_path, password=None):
        zip_file = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
        if password:
            zip_file.setpassword(password.encode())
        for root, dirs, files in os.walk(file_path):
            for file in files:
                zip_file.write(os.path.join(root, file), 
                               os.path.relpath(os.path.join(root, file), 
                               os.path.join(file_path, '..')))
        zip_file.close()

    # 解压缩文件方法
    @staticmethod
    def unzip(zip_path, file_path):
        zip_file = zipfile.ZipFile(zip_path, 'r')
        for file in zip_file.namelist():
            zip_file.extract(file, file_path)
        zip_file.close()

    # 解压压缩包中指定文件
    @staticmethod
    def unzip_file(zip_path, file_name, file_path):
        zip_file = zipfile.ZipFile(zip_path, 'r')
        zip_file.extract(file_name, file_path)
        zip_file.close()

    # 解压缩文件夹方法
    @staticmethod
    def unzip_dir(zip_path, dir_path):
        zip_file = zipfile.ZipFile(zip_path, 'r')
        for file in zip_file.namelist():
            zip_file.extract(file, dir_path)
        zip_file.close()

    # 查看压缩文件内容方法，返回压缩文件内容列表
    @staticmethod
    def zip_content(zip_path):
        zip_file = zipfile.ZipFile(zip_path, 'r')
        return zip_file.namelist()

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

def open_file(file_path):
    """根据文件类型打开文件（图片或文本）。"""
    try:
        # 检查文件扩展名
        ext = os.path.splitext(file_path)[-1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            open_image_file(file_path)
        elif ext in ['.txt', '.json', '.log', '.xml']:
             open_text_file(file_path)
        else:
            logger.warning(f"不支持的文件类型：{ext}")
    except Exception as e:
        logger.error(f"打开文件 {file_path} 时出错：{e}")

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
