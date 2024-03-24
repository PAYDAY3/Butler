import os
import shutil
import datetime
import time

# 上次执行时间的初始化为程序启动时的时间
last_execution_time = datetime.datetime.now()

def delete_temp_files():
    global last_execution_time
    directory = "./temp"

    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 删除文件
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
                    
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # 删除子目录及其下所有文件
            shutil.rmtree(dir_path)
            print(f"Deleted directory: {dir_path}")

    print("All files and directories inside 'temp' directory have been deleted.")
                                                                                
    # 更新上次执行时间为当前时间
    last_execution_time = datetime.datetime.now()

# 检查是否已经过了五天，如果是则执行删除操作
def check_and_delete():
    global last_execution_time
    current_time = datetime.datetime.now()
    if (current_time - last_execution_time).days >= 5:
        delete_temp_files()

# 主循环，每秒钟检查一次是否需要执行删除操作
while True:
    check_and_delete()
    time.sleep(1)