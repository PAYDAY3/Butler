import os
import hashlib
import shutil

def get_file_hash(file_path):
    """
    计算文件的SHA-256哈希值
    :param file_path: 文件路径
    :return: 文件的SHA-256哈希值
    """
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def organize_and_move_duplicates(folder_path):
    """
    组织文件并移动重复文件
    :param folder_path: 需要组织的文件夹路径
    """
    # 创建一个字典来存储基于文件扩展名的目标文件夹
    extension_folders = {}

    # 如果不存在，创建“Duplicates”文件夹
    duplicates_folder = os.path.join(folder_path, 'Duplicates')
    os.makedirs(duplicates_folder, exist_ok=True)

    # 创建一个字典来存储文件哈希值
    file_hashes = {}

    # 遍历文件夹中的文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            # 获取文件扩展名
            _, extension = os.path.splitext(filename)
            extension = extension.lower()  # 将扩展名转换为小写
            
            # 确定目标文件夹
            if extension in extension_folders:
                destination_folder = extension_folders[extension]
            else:
                destination_folder = os.path.join(folder_path, extension[1:])  # 去掉扩展名前的点
                os.makedirs(destination_folder, exist_ok=True)
                extension_folders[extension] = destination_folder
            
            # 计算文件哈希值
            file_hash = get_file_hash(file_path)
            
            # 检查是否有重复文件
            if file_hash in file_hashes:
                # 文件是重复的，将其移动到“Duplicates”文件夹
                shutil.move(file_path, os.path.join(duplicates_folder, filename))
                print(f"已将重复文件 {filename} 移动到 Duplicates 文件夹。")
            else:
                # 存储文件哈希值
                file_hashes[file_hash] = filename
                # 将文件移动到目标文件夹
                shutil.move(file_path, destination_folder)
                print(f"已将 {filename} 移动到 {destination_folder}")

if __name__ == "__main__":
    folder_path = input("请输入要组织的文件夹路径: ")
    organize_and_move_duplicates(folder_path)
