from snowboy import snowboydecoder
from package import Logging
import os
import time
import subprocess  # 导入 subprocess 库

# 设置 Snowboy 模型路径
MODEL_PATH = "snowboy/jarvis.pmdl"

# 设置要运行的文件路径
FILE_TO_RUN = "jarvis.py" 
FILE_TO_RUN_1 = "scheduled_tasks.py"

#设置其他参数
SENSITIVITY = 0.5  # 灵敏度
CHANNELS = 1
RATE = 16000
CHUNK_SIZE = 1024

logging = Logging.getLogger(_name_)

#创建 Snowboy 检测器
detector = snowboydecoder.HotwordDetector(MODEL_PATH, sensitivity=SENSITIVITY)

#定义回调函数
def detected_callback():
    print("唤醒词检测到！")
    
    # 运行指定文件
    try:
        subprocess.run([FILE_TO_RUN])
        logging.info(f"文件 '{FILE_TO_RUN}' 已运行。")
        time.sleep(5)  # 这里设置延迟时间为5秒
        
        subprocess.run([FILE_TO_RUN_1]) 
        logging.info(f"文件 '{FILE_TO_RUN_1}' 已运行。")                
    except FileNotFoundError:
        logging.error(f"文件 '{FILE_TO_RUN}' 未找到。")
    except Exception as e:
        logging.error(f"运行文件出错: {e}")

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
