import os
import hashlib
from jarvis.jarvis import takecommand
folder_path = "./my_package/downloaded"

def get_file_hash(file_path):
    """
    计算文件的SHA-256哈希值
    :param file_path: 文件路径
    :return: 文件的SHA-256哈希值
    """
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def organize_files(folder_path):
    """
    整理指定文件夹中的文件，按字母大小顺序排列，名字长短
    :param folder_path: 需要整理的文件夹路径
    """
    # 创建一个字典来存储基于文件扩展名的目标文件夹
    extension_folders = {}

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
                # 文件是重复的，重命名文件
                file_counter = 2
                new_filename = filename
                while os.path.exists(os.path.join(destination_folder, new_filename)):
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}_{file_counter}{ext}"
                    file_counter += 1
                os.rename(file_path, os.path.join(destination_folder, new_filename))
                print(f"已将重复文件 {filename} 重命名为 {new_filename} 在 {destination_folder}")
            else:
                # 存储文件哈希值
                file_hashes[file_hash] = filename
                # 移动文件到目标文件夹
                new_file_path = os.path.join(destination_folder, filename)
                if not os.path.exists(new_file_path):
                    os.rename(file_path, new_file_path)
                    print(f"已将 {filename} 移动到 {destination_folder}")
                else:
                    print(f"{filename} 已存在于 {destination_folder}")

    # 对每个目标文件夹中的文件进行排序
    for folder in extension_folders.values():
        sorted_files = sorted(os.listdir(folder), key=lambda x: (len(x), x))
        for i, filename in enumerate(sorted_files):
            old_path = os.path.join(folder, filename)
            new_path = os.path.join(folder, f"{i+1:03d}_{filename}")
            os.rename(old_path, new_path)


if __name__ == "__main__":
    command = takecommand()
    # 解析用户指令
    if command and "整理" in command:
        # 提取用户指令中的文件夹路径
        folder_path = command.split("整理")[-1].strip()
        organize_files(folder_path, command, {})
    else:
        print("无效指令，请说 '整理 [文件夹路径]'")
