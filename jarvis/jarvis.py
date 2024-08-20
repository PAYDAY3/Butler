import os
import sys
import time
import importlib
import importlib.util
#import speech_recognition as sr
import pygame
import time
import json
import pyttsx3
import datetime
import subprocess
import tkinter as tk
from tkinter import messagebox
from pydub import AudioSegment
from pydub.playback import play
import openai
from my_snowboy.snowboydecoder import HotwordDetector
#临时文件
import shutil
import tempfile
import concurrent.futures
from functools import lru_cache
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import azure.cognitiveservices.speech as speechsdk

from my_package.thread import process_tasks
import binary_extensions
from my_package.TextEditor import TextEditor
from my_package.virtual_keyboard import VirtualKeyboard
from my_package import Logging
from my_package.schedule_management import schedule_management
from jarvis.CommandPanel import CommandPanel

# OpenAI API密钥
openai.api_key = "YOUR_OPENAI_API_KEY"

def preprocess(text):
    # 使用 OpenAI API 对输入进行编码
    inputs = openai.Completion.create(
        prompt=text,
        max_tokens=512,
        stop=None,
        temperature=0
    )['choices'][0]['text']
    return inputs

def generate_response(text):
    input_ids = preprocess(text)
                                                        
    # 使用 OpenAI API 生成响应
    response = openai.Completion.create(
        prompt=input_ids,
        max_tokens=150,
        temperature=0.5
    )['choices'][0]['text']
    return response

# 对话提示
print("我是你的聊天助手。")

# 创建一个简单的对话循环
while True:
    user_input = input(">>> ")
    if user_input.lower() in ["退出", "结束"]:
        break
    response = generate_response(user_input)
    print("Chatbot:", response)
    
    
# 定义音频文件路径
JARVIS_AUDIO_FILE = "./my_snowboy/resources/jarvis.wav"
OUTPUT_FILE = "./temp.wav"
FINAL_OUTPUT_FILE = "./final_output.wav"

# 创建语音合成引擎
engine = pyttsx3.init()

def speak(audio):
    # 合成语音
    engine.say(audio)
    engine.runAndWait()  # 播放合成语音

    # 加载音效文件
    jarvis_sound = AudioSegment.from_wav(JARVIS_AUDIO_FILE)

    # 加载合成语音文件
    synthetic_speech = AudioSegment.from_wav(OUTPUT_FILE)

    # 调整音量
    synthetic_speech = synthetic_speech.apply_gain(10)  # 提高合成语音的音量
    jarvis_sound = jarvis_sound.apply_gain(-10)  # 降低音效的音量

    # 添加立体声效果
    synthetic_speech = add_stereo_effect(synthetic_speech)
    
    # 添加回声效果
    combined_sound = add_echo_effect(synthetic_speech)
    
    # 合并音频片段
    combined_sound = jarvis_sound.overlay(synthetic_speech)

    # 添加混响效果
    combined_sound = combined_sound.apply_reverb(reverb=AudioSegment.reverb(duration=1000))

    # 保存混合后的音频
    combined_sound.export(FINAL_OUTPUT_FILE, format="wav")

    # 播放混合后的音频
    play(FINAL_OUTPUT_FILE)

    # 删除临时文件
    os.remove(OUTPUT_FILE)

# 初始化日志
#   log_file = "program_log.txt"
#   logging.basicConfig(filename=log_file, level=logging.DEBUG)

logging = Logging.getLogger(__name__)

# 定义唤醒词和其他全局变量
WAKE_WORD = "jarvis"
Input_command = ">>> "
program_folder = ["./program", "./tools"]
model = "my_Snowboy/jarvis.umdl"  # Snowboy 模型文件路径

# 语音识别
def takecommand():
    # 替换为你的 Azure 订阅密钥和服务区域
    speech_key = "your_subscription_key"
    service_region = "chinaeast2"

    # 配置 Azure 语音服务
    speech_config.speech_synthesis_language = "zh-CN"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("请说话...")

    try:
        # 开始语音识别
        result = recognizer.recognize_once()

        # 处理识别结果
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            query = result.text
            print('User: ' + query + '\n')
            return query
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("对不起，我没有听清楚，请再说一遍。")
            return None
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"语音识别取消: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"错误详情: {cancellation_details.error_details}")
            return None

    except Exception as e:
        print(f"语音识别出错: {e}")
        logging.error(f"语音识别出错: {e}")
        return None    

# 创建 Snowboy 监听器
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5, audio_gain=1)
detector.start(takecommand)

class ProgramHandler(FileSystemEventHandler):
    def __init__(self, program_folder, external_folders=None):
        self.program_folder = program_folder
        self.external_folders = external_folders or []
        self.programs_cache = {}
        self.programs = self.open_programs()

    def on_modified(self, event):
        if event.src_path.endswith(('.py', 'invoke.py')) or event.src_path.split('.')[-1] in binary_extensions:
            self.programs = self.open_programs.clear_cache()()

    def on_created(self, event):
        if event.src_path.endswith(('.py', 'invoke.py')) or event.src_path.split('.')[-1] in binary_extensions:
            self.programs = self.open_programs.clear_cache()()

    @lru_cache(maxsize=128)
    def open_programs(self):
        programs_cache = {}
        global all_folders
        all_folders = [self.program_folder] + self.external_folders
        
        # 检查程序文件夹是否存在
        for folder in all_folders:
            if not os.path.exists(folder):
                print(f"文件夹 '{folder}' 未找到。")
                logging.info(f"文件夹 '{folder}' 未找到。")
                continue
                
            programs = {}
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith(('.py', 'invoke.py')) or file.split('.')[-1] in binary_extensions:
                        program_name = os.path.basename(root) + '.' + file[:-3]
                        program_path = os.path.join(root, file)

                        if program_name in self.programs_cache:
                            program_module = self.programs_cache[program_name]
                        else:
                            try:
                                spec = importlib.util.spec_from_file_location(program_name, program_path)
                                program_module = importlib.util.module_from_spec(spec)
                                sys.modules[program_name] = program_module
                                spec.loader.exec_module(program_module)
                                self.programs_cache[program_name] = program_module
                            except ImportError as e:
                                print(f"加载程序模块 '{program_name}' 时出错：{e}")
                                logging.info(f"加载程序模块 '{program_name}' 时出错：{e}")
                                continue

                            if not hasattr(program_module, 'run'):
                                print(f"程序模块 '{program_name}' 无效。")
                                logging.info(f"程序模块 '{program_name}' 无效。")
                                continue

                        programs[program_name] = program_module
                    
        # 按字母顺序排序程序模块
        programs = dict(sorted(programs.items()))
        return programs
        
@lru_cache(maxsize=128)       
def execute_program(program_name, handler):
    try:
        module_path = f"{handler.program_folder}.{program_name}"
        program_module = importlib.import_module(module_path)
        program_module.run()  # 此处调用了程序模块的 run 函数
    except ImportError as error:
        print(f"导入模块失败: {error}")
        logging.error(f"导入模块失败: {error}")
    except AttributeError:
        print(f"模块中未找到运行函数: {program_name}")
        logging.error(f"模块中未找到运行函数: {program_name}")
        
def handle_user_command(command, program_mapping, handler, programs):
    if command.startswith("打开"):
        program_name = command[3:].strip()
        if program_name in program_mapping:
            execute_program(program_mapping[program_name], handler)
        else:
            print(f"未找到程序 '{program_name}'")
    elif command in program_mapping:
        execute_program(program_mapping[command], handler)
    elif command.startswith(("进行", "运行")):
        program_name = command[2:].strip()
        if program_name in handler.programs:
            execute_program(handler.programs[program_name])
        else:
            print(f"未找到程序 '{program_name}'")        
    elif "退出" in command or "结束" in command:
        logging.info(f"{program_folder}程序已退出")
        speak(f"{program_folder}程序已退出")
        running = False
    else:
        print("未知指令，请重试")
        logging.warning("未知指令")
        time.sleep(3)
        match_program(wake_command, programs, program_folder)

# 创建临时文件并移动到目标文件夹
def manage_temp_files():
    temp_dir = tempfile.gettempdir()
    target_dir = "./temp"
    temp_file_path = tempfile.mktemp(suffix=".txt", dir=temp_dir)

    with open(temp_file_path, 'w') as file:
        file.write("这是临时文件中的数据")

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    shutil.move(temp_file_path, target_dir)

# 匹配和执行程序
def match_and_run_program(wake_command, programs, program_folder):
    matched_program = None
    for program_name, program_module in programs.items():
        if program_name in wake_command:
            matched_program = program_module
            break

    if matched_program is None:
        for module_file in os.listdir(program_folder):
            if module_file.endswith(('.py', 'invoke.py')) or file.split('.')[-1] in binary_extensions:
                if module_file in wake_command:
                    module_path = f"{program_folder}.{module_file[:-3]}"
                    try:
                        program_module = importlib.import_module(module_path)
                        program_module.run()
                        matched_program = program_module
                        break
                    except ImportError as error:
                        print(f"导入模块失败: {error}")
                        logging.error(f"导入模块失败: {error}")

    return matched_program
    
def process_voice_input():
    display_subtitle("语音输入模式已激活，请开始说话...")
    wake_command = takecommand().lower()
    print(f"请输入命令: {wake_command}")
    display_subtitle(f"语音输入: {wake_command}")
    logging.info("Voice command: " + wake_command)
    return wake_command

def process_text_input():
    display_subtitle("文字手写输入模式已激活。输入 2 返回语音输入模式。")
    user_input = input("请输入命令: ").lower()
    print(f"请输入命令: {user_input}")
    display_subtitle(f"文字手写输入: {user_input}")
    logging.info("Text input: " + user_input)
    return user_input       
    
@lru_cache(maxsize=128)
def main():
    handler = ProgramHandler(program_folder)
    observer = Observer()
    observer.schedule(handler, program_folder, recursive=True)
    observer.start()

    program_mapping = {
        "邮箱": "e-mail.py",
        "播放音乐": "music.py",
        "虚拟键盘": "virtual_keyboapy.py",
        "组织文件": "Organizepy.py",
        "爬虫": "crawlpy.py",
        "终端": "terminpy.py",
        "加密": "encrypt.py",
        "文本编辑器": "TextEditor.py",
        "物体识别": "PictureRecognition.py",
        "日程管理": "schedule_management.py",
        "二维码识别": "QR-Code-Recognitipy.py",
        "网络程序": "network_apy.py",
        "天气预报": "weathpy.py",
        "翻译": "translators.py",
        "文件转换器": "file_converter.py",
        "帐号登录": "AccountPassword",
        # 继续添加其他命令和程序的映射关系
    }

    conversation_history = []

    process_tasks()  # 运行多线程程序
    schedule_management()
    manage_temp_files()

    global matched_program
    matched_program = None
    pygame.init()  # 初始化 Pygame

    programs = open_programs(program_folder)
    print("等待唤醒词")
    if not programs:
        print("没有找到程序模块")
        return
    use_voice_input = True
    running = True  # 控制程序是否继续运行的标志
    while running:
        detector = HotwordDetector(model, sensitivity=0.5, audio_gain=1)
        detector.start(detected_callback=takecommand, interrupt_check=lambda: False, sleep_time=0.03)
        detector.terminate()
        
        if use_voice_input: 
            wake_command = takecommand()
           
            if wake_command in ["切换文字输入", "1"]:
                use_voice_input = False
                display_subtitle("已切换到文字手写输入模式")
            elif WAKE_WORD in wake_command or wake_command.startswith("打开"):
                display_subtitle("已唤醒，等待命令...")
                logging.info("已唤醒，等待命令")
                time.sleep(1)

                command = wake_command.replace(WAKE_WORD, '').strip() if WAKE_WORD in wake_command else wake_command
                if command.startswith("打开"):
                    program_name = command[2:].strip()
                    if program_name in program_mapping:
                        execute_program(program_mapping[program_name], handler)
                    else:
                        print(f"未找到程序 '{program_name}'")
                        logging.info(f"未找到程序 '{program_name}'")
                else:
                    print("未知指令，请重试")
                    logging.warning("未知指令")

                handle_user_command(command, program_mapping, handler, programs)
            else:
                match_and_run_program(wake_command, programs, program_folder)
        else:
            user_input = process_text_input()
            
            if user_input.startswith("打开"):
                program_name = user_input[2:].strip()
                if program_name in program_mapping:
                    execute_program(program_mapping[program_name], handler)
                else:
                    print(f"未找到程序 '{program_name}'")
                    logging.info(f"未找到程序 '{program_name}'")
            else:
                print("未知指令，请重试")
                logging.warning("未知指令")

            if user_input == "2":
                use_voice_input = True
                display_subtitle("已切换回语音输入模式")
            elif "退出" in user_input or "结束" in user_input:
                display_subtitle("程序已退出")
                logging.info(f"用户已退出{program_folder}程序")
                running = False
            else:
                handle_user_command(user_input, program_mapping, handler, programs)

    observer.stop()
    observer.join()
    if not running: # 退出程序
        # 打开另一个程序
        os.system("python Bide_one's_time.py")
            
    # 创建主窗口
    root = tk.Tk()
    root.title("jarvis交互面板")
    root.geometry("800x600")

    # 创建交互式命令行面板
    panel = CommandPanel(root, [])  # 使用 CommandPanel 类创建一个实例
    panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # 启动主事件循环
    root.mainloop()
    
if __name__ == "__main__":  
    main()
