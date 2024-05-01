import os
import shutil
import datetime

def delete_temp_files():
    global last_execution_time
    directory = "./temp"

    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 删除文件
            os.remove(file_path)
            print(f"删除文件: {file_path}")
                    
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # 删除子目录及其下所有文件
            shutil.rmtree(dir_path)
            print(f"删除目录: {dir_path}")

    print("“temp”目录下的所有文件和目录已被删除")
                                                                                
