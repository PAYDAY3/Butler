from my_snowboy.snowboydecoder import snowboydecoder
import os
import time
import subprocess  # 导入 subprocess 库

# 设置 Snowboy 模型路径
MODEL_PATH = "your_model_path/your_model.pmdl"

# 设置要运行的文件路径
FILE_TO_RUN = "jarvis.py" 
FILE_TO_RUN_1 = "scheduled_tasks.py"

#设置其他参数
SENSITIVITY = 0.5  # 灵敏度
CHANNELS = 1
RATE = 16000
CHUNK_SIZE = 1024

#创建 Snowboy 检测器
detector = snowboydecoder.HotwordDetector(MODEL_PATH, sensitivity=SENSITIVITY)
def is_process_running(process_name):
    """
    检查指定进程是否正在运行
    """
    for proc in os.popen("ps aux | grep " + process_name):
        if process_name in proc:
            return True
    return False
        
#定义回调函数
def detected_callback():
    print("唤醒词检测到！")
    
    # 运行指定文件
    try:
        # 检查指定进程是否已运行
        if not is_process_running(FILE_TO_RUN.split("/")[-1]):  # 使用文件名称进行检查
            subprocess.run(FILE_TO_RUN)  # 使用 subprocess.run 运行文件
            print("文件已运行。")
        else:
            print(f"进程 '{FILE_TO_RUN_.split('/')[-1]}' 正在运行。")  
        if not is_process_running(FILE_TO_RUN_1.split("/")[-1]):  # 使用文件名称进行检查
            subprocess.run(FILE_TO_RUN_1)  # 使用 subprocess.run 运行文件
            print("文件已运行。")
        else:
            print(f"进程 '{FILE_TO_RUN_1.split('/')[-1]}' 正在运行。")  
                        
    except FileNotFoundError:
        print(f"文件 '{FILE_TO_RUN}' 未找到。")
    except Exception as e:
        print(f"运行文件出错: {e}")

    # 关闭唤醒程序
    detector.terminate()
    print("唤醒程序已关闭。")
    # 等待直到下一个5分钟周期开始
    next_interval_start = (int(time.time() / 300) + 1) * 300  # 计算下一个5分钟周期的开始时间
    time.sleep(next_interval_start - time.time())  # 等待直到下一个周期开始
    
#启动持续监听
print("正在监听...")
detector.start(detected_callback=detected_callback,
              audio_recorder=snowboydecoder.AudioRecorder(
                  audio_source=snowboydecoder.AudioSource(
                      recorder_instance=snowboydecoder.Recorder(
                          rate=RATE,
                          channels=CHANNELS,
                          chunk_size=CHUNK_SIZE,
                          sleep_time=0.03,
                      )
                  )
              )
         )
