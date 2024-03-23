
import os
import sys
import time
import importlib
import speech_recognition as sr
import pygame
import time
import logging
import json
import pyttsx3
import datetime
from my_snowboy.snowboydecoder import snowboydecoder
#临时文件
import shutil
import tempfile
import concurrent.futures

import threading
from thread import process_tasks

from my_package.date import date
from my_package.speak import wishme
from TextEditor import TextEditor
from my_package.virtual_keyboard import VirtualKeyboard
from my_package.algorithm import greedy_activity_selection

# Snowboy 模型文件路径
model = "my_Snowboy/jarvis.umdl"

# pocketsphinx 参数配置
config = {
    "verbose": False,
    "audio_gain": 1.5,
    "keyphrase": "jarvis",
    "kws_threshold": 1e-5    
}

# 初始化语音识别器和文本到语音引擎
recognizer = sr.Recognizer()
engine = pyttsx3.init()# 为语音合成创建一个引擎实例

def speak(audio):
    engine.say(audio)# 将需要语音合成的文本传递给引擎
    engine.runAndWait()# 播放语音

# 初始化日志
log_file = "program_log.txt"
logging.basicConfig(filename=log_file, level=logging.DEBUG)

# 定义唤醒词
WAKE_WORD = "jarvis"

Input_command = ">>> "
program_folder = "/program"

# 唤醒成功，开始监听用户命令
wake_command = recognize_sphinx().lower()

# 语音识别
def takecommand():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("请说话...")
        recognizer.pause_threshold = 1  # 静态能量阈值
        recognizer.dynamic_energy_adjustment_damping = 0.15 # 调整阈值的平滑因子
        recognizer.dynamic_energy_ratio = 1.5  # 阈值调整比率
        recognizer.operation_timeout = 5  # 最长等待时间（秒）
        recognizer.energy_threshold = 4000      # 设置音量阈值
        recognizer.dynamic_energy_threshold = True  # 自动调整音量阈值
        recognizer.default = "model"
        audio = recognizer.listen(source, phrase_time_limit=5)
        # 将录制的音频保存为临时文件
        with tempfile.NamedTemporaryFile(delete=False) as f:
            audio_file_path = f.name + ".wav"
            f.write(audio.get_wav_data())
    return audio_file_path 
    try:
        print("Recognizing...")  # 识别中...
        query = recognizer.recognize_sphinx(audio, language='zh-CN')
        print('User: ' + query + '\n')
        return query     
    except Exception as e:
        print("对不起，我没有听清楚，请再说一遍。")
        speak("对不起，我没有听清楚，请再说一遍。")
        query = None
        return query
    except sr.RequestError as error:
        print(f"语音识别请求出错：{error}")
        logging.error(f"语音识别请求出错：{error}")
        return ""

# 创建 Snowboy 监听器
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5, audio_gain=1)
detector.start(takecommand)

# 主程序逻辑
def main_program_logic(program_folder):
    # 获取程序模块字典
    programs = open_programs(program_folder)
    # 定义程序映射关系字典
    program_mapping = {
        "打开浏览器": "browser_program",
        "播放音乐": "music_program",
        "查看日历": "calendar_program"
        # 在这里继续添加其他命令和程序的映射关系
    }
    
    running = True
    while running:
        try:
            wake_command = takecommand().lower() #recognize_sphinx(takecommand()).lower()
            program_file_name = program_mapping.get(wake_command, None)
            if program_file_name:
                print(f"正在执行命令: {wake_command}")
                speak(f"正在执行命令: {wake_command}")
                logging.info(f"{datetime.datetime.now()} - {wake_command}")
                program_module = programs.get(program_file_name, None)
                if program_module:
                    program_module.run()  # 调用对应程序的逻辑
                else:
                    print(f"未找到程序: {program_file_name}")
                    speak(f"未找到程序: {program_file_name}")

            elif "退出" in wake_command or "结束" in wake_command:
                print(f"{program_folder}程序已退出")
                speak(f"{program_folder}程序已退出")
                logging.info(f"{datetime.datetime.now()} - 正在退出{program_folder}")
                sys.exit()
            else:
                print("未知命令")
                speak("未知命令")
                logging.info(f"{datetime.datetime.now()} - 未知命令: {wake_command}")

        except Exception as error:
            logging.error(f"{datetime.datetime.now()} - 程序出现异常: {error}")
            print(f"程序出现异常: {error}")
            speak(f"程序出现异常: {error}")
            
# 打开程序模块
def open_programs(program_folder):
    programs = {}
    for program_file in os.listdir(program_folder):
        if program_file.endswith('.py'):
            program_name = program_file[:-3]
            try:
                program_module= importlib.import_module(f"{program_folder}.{program_name}")
                programs[program_name] = program_module
            except ImportError as error:
                logging.error(f"导入模块 {program_name} 失败：{error}")
    return programs

 # 主函数
def main():
    # 获取系统的临时文件夹路径
    temp_dir = tempfile.gettempdir()

    # 指定要保存临时文件的文件夹路径
    target_dir = "./temp"

    # 创建一个临时文件
    temp_file_path = tempfile.mktemp(suffix=".txt", dir=temp_dir)

    # 在临时文件中写入数据
    with open(temp_file_path, 'w') as file:
        file.write("这是临时文件中的数据")

    # 将临时文件移动到目标文件夹
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    shutil.move(temp_file_path, target_dir)
    
    global matched_program
    matched_program = None
    pygame.init()  # 初始化 Pygame
    wen_jian = 'program_folder'
    programs = open_programs(wen_jian)
    print("等待唤醒词")
    if not programs:
        print("没有找到程序模块")
        return ""

    running = True  # 控制程序是否继续运行的标志
    while running:

        # 开始监听
        detector.start(detected_callback=takecommand,
                       interrupt_check=lambda: False,
                       sleep_time=0.03)

        # 程序结束时停止监听
        detector.terminate()

        wake_command = takecommand().lower()#    recognize_sphinx(takecommand()).lower()
        user_input = None
        print("等待唤醒词")
        logging.info("等待唤醒词")
        if "退出" in wake_command or "结束" in wake_command:
            print("程序已退出")
            logging.info("用户已退出程序")
            running = False  # 设置标志为 False，用于退出主循环

    if not running:
        # 打开另一个程序
        os.system("python Bide_one's_time.py") 
                 
        if "手动输入" in wake_command:
            keyboard = VirtualKeyboard()
            # 打开虚拟键盘
            keyboard.open()
            # 获取虚拟键盘输入的字符
            input_text = keyboard.get_input()
            user_input = input_text.strip()
            logging.info("用户手动输入：" + user_input)
            if "退出" in user_input or "结束" in user_input:
                print("程序已退出")
                logging.info(f"{datetime.datetime.now()} - 用户已退出程序手写输入")
                running = False  # 设置标志为 False，用于退出主循环
                return None
            return user_input

        if WAKE_WORD in wake_command:
            print("已唤醒，等待命令...")
            logging.info(f"{datetime.datetime.now()} - 已唤醒，等待命令")
            time.sleep(1)

            # 通过文本交流获取用户输入
            query = input(Input_command)
            response_text = takecommand(query).lower()

            user_command = response_text[len(WAKE_WORD):].strip()  
            # 对用户输入进行处理，执行特定操作
            if "打开程序" in user_command:
                program_name = response_text.replace("打开程序", "").strip()
                if program_name in programs:
                    program_module = programs[program_name]
                    if program_module is not None:
                        program_module.run()
                    else:
                        print(f"未找到程序：{program_name}")
                else:
                    print(f"未找到程序：{program_name}")

            elif "退出" in user_command or "结束" in user_command:
                print("程序已退出")
                logging.info("用户已退出程序")
                running = False  # 设置标志为 False，用于退出主循环
            else:
                print("未知指令，请重试")
                logging.warning("未知指令")
                time.sleep(3)
                # 在这里添加后续的命令处理逻辑

                # 检查命令是否匹配程序模块
                matched_program = None
                for program_name, program_module in programs.items():
                    if program_name in wake_command:
                        matched_program = program_module
                        break  # 正常退出循环

                if matched_program is None:
                    # 检查命令是否匹配到模块文件名
                    for module_file in os.listdir(program_folder):
                        if module_file.endswith('.py'):
                            if module_file in wake_command:
                                module_path = f"{program_folder}.{module_file[:-3]}"
                                try:
                                    program_module = importlib.import_module(module_path)
                                    program_module.run()  # 此处调用了程序模块的 run 函数
                                    continue
                                except ImportError as error:
                                    print(f"导入模块失败: {error}")
                                    logging.error(f"导入模块失败: {error}")

# 定义活动的开始时间和结束时间列表
start_times = [1, 3, 0, 5, 8, 5]
finish_times = [2, 4, 6, 7, 9, 9]
if __name__ == "__main__":
    wishme()# 执行程序初始化逻辑
    # 调用贪心算法函数，获取选择的活动列表
    selected_activities = greedy_activity_selection(start_times, finish_times)
    # 打印选择的活动列表
    print(selected_activities)    
    while True:
        try:
           
            # 执行主程序的逻辑
            main()
            # 执行主程序的逻辑
            main_program_logic("program_folder")
            process_tasks()# 运行多线程程序
            # 从文件中加载程序映射
            mapping = load_program_mapping()
            print(mapping)
            manual_command = manual_input()  # 执行主程序的逻辑
            # 在这里根据输入的命令执行相应操作
            if "退出" in manual_command or "结束" in manual_command:
                print("程序已退出")
                logging.info("程序已退出")
                break
            # 添加更多命令处理逻辑
        except KeyboardInterrupt:
            print("用户中断程序")
            logging.info("用户中断程序")
        except ImportError as error:
            logging.error(f"导入模块失败: {error}")
        except Exception as error:
            print(f"程序发生异常：{error}")
            logging.info(f"程序发生异常：{error}")
        finally:
            try:
                main_program_logic("program_folder")  # 执行主程序的逻辑
            except Exception as error:
                print(f"程序发生异常：{error}")
                logging.info(f"程序发生异常：{error}")
        query = takecommand().lower()
        if "time" in query:
          time()

        elif "date" in query:
            date()

        elif "who are you" in query:#译文:你是谁
            speak("")#增加程序介绍
            print("")

        elif "how are you" in query:#译文:你好吗?
            speak("I'm fine sir, What about you?")#译文：我很好，先生，你呢?
            print("I'm fine sir, What about you?")

        elif 'play music' in query:
            music_folder = Your_music_folder_path
            music = [music1, music2, music3, music4, music5]
            random_music = music_folder + random.choice(music) + '.mp3'
            os.system(random_music)     
            speak('Okay, here is your music! Enjoy!')
