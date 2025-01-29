import os
import sys
import time
import importlib
import importlib.util
#import speech_recognition as sr
import pygame
import json
import pyttsx3
import datetime
import subprocess
import tkinter as tk
from tkinter import messagebox
from pydub import AudioSegment
from pydub.playback import play
import openai
from snowboy import snowboydecoder
import shutil
import tempfile
import concurrent.futures
from functools import lru_cache
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import azure.cognitiveservices.speech as speechsdk

from package.thread import process_tasks
import binary_extensions
from package.TextEditor import TextEditor
from package.virtual_keyboard import VirtualKeyboard
from package import Logging
from package.schedule_management import schedule_management
from jarvis.CommandPanel import CommandPanel
from plugin.plugin import plugin

class Jarvis:
    def __init__(self):
        self.openai_api_key = "YOUR_OPENAI_API_KEY"
        openai.api_key = self.openai_api_key
        self.engine = pyttsx3.init()
        self.logging = Logging.getLogger(__name__)
        self.WAKE_WORD = "jarvis"
        self.program_folder = ["./program", "./tools"]
        self.model = "my_Snowboy/jarvis.umdl"
        self.program_mapping = {
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
            "帐号登录": "AccountPassword.py",
        }
        self.conversation_history = []
        self.running = True
        self.use_voice_input = True
        self.matched_program = None

    def preprocess(self, text):
        inputs = openai.Completion.create(
            prompt=text,
            max_tokens=512,
            stop=None,
            temperature=0
        )['choices'][0]['text']
        return inputs

    def generate_response(self, text):
        input_ids = self.preprocess(text)
        response = openai.Completion.create(
            prompt=input_ids,
            max_tokens=150,
            temperature=0.5
        )['choices'][0]['text']
        return response
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

    def takecommand(self):
        speech_key = "your_subscription_key"
        service_region = "chinaeast2"
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_language = "zh-CN"
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

        print("请说话...")

        try:
            result = recognizer.recognize_once()
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
            self.logging.error(f"语音识别出错: {e}")
            return None

    def handle_user_command(self, command, handler, programs):
        if command.startswith("打开"):
            program_name = command[3:].strip()
            if program_name in self.program_mapping:
                self.execute_program(self.program_mapping[program_name], handler)
            else:
                print(f"未找到程序 '{program_name}'")
        elif command in self.program_mapping:
            self.execute_program(self.program_mapping[command], handler)
        elif command.startswith(("进行", "运行")):
            program_name = command[2:].strip()
            if program_name in handler.programs:
                self.execute_program(handler.programs[program_name])
            else:
                print(f"未找到程序 '{program_name}'")
        elif "退出" in command or "结束" in command:
            self.logging.info(f"{self.program_folder}程序已退出")
            self.speak(f"{self.program_folder}程序已退出")
            self.running = False
        else:
            print("未知指令，请重试")
            self.logging.warning("未知指令")
            time.sleep(3)
            self.match_program(command, programs, self.program_folder)

    @lru_cache(maxsize=128)
    def open_programs(self, program_folder, external_folders=None):
        programs_cache = {}
        all_folders = [program_folder] + (external_folders or [])
        
        for folder in all_folders:
            if not os.path.exists(folder):
                print(f"文件夹 '{folder}' 未找到。")
                self.logging.info(f"文件夹 '{folder}' 未找到。")
                continue
                
            programs = {}
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith(('.py', 'invoke.py')) or file.split('.')[-1] in binary_extensions:
                        program_name = os.path.basename(root) + '.' + file[:-3]
                        program_path = os.path.join(root, file)

                        if program_name in programs_cache:
                            program_module = programs_cache[program_name]
                        else:
                            try:
                                spec = importlib.util.spec_from_file_location(program_name, program_path)
                                program_module = importlib.util.module_from_spec(spec)
                                sys.modules[program_name] = program_module
                                spec.loader.exec_module(program_module)
                                programs_cache[program_name] = program_module
                            except ImportError as e:
                                print(f"加载程序模块 '{program_name}' 时出错：{e}")
                                self.logging.info(f"加载程序模块 '{program_name}' 时出错：{e}")
                                continue

                            if not hasattr(program_module, 'run'):
                                print(f"程序模块 '{program_name}' 无效。")
                                self.logging.info(f"程序模块 '{program_name}' 无效。")
                                continue

                        programs[program_name] = program_module
                    
        programs = dict(sorted(programs.items()))
        return programs
    
    @lru_cache(maxsize=128)
    def execute_program(self, program_name, handler):
        try:
            module_path = f"{handler.program_folder}.{program_name}"
            program_module = importlib.import_module(module_path)
            program_module.run()
        except ImportError as error:
            print(f"导入模块失败: {error}")
            self.logging.error(f"导入模块失败: {error}")
        except AttributeError:
            print(f"模块中未找到运行函数: {program_name}")
            self.logging.error(f"模块中未找到运行函数: {program_name}")

    def main(self):
        plugin()
        handler = self.ProgramHandler(self.program_folder)
        observer = Observer()
        observer.schedule(handler, self.program_folder, recursive=True)
        observer.start()

        process_tasks()
        schedule_management()
        self.manage_temp_files()

        programs = self.open_programs(self.program_folder)
        print("等待唤醒词")
        if not programs:
            print("没有找到程序模块")
            return
        
        while self.running:
            detector = snowboydecoder.HotwordDetector(self.model, sensitivity=0.5, audio_gain=1)
            detector.start(detected_callback=self.takecommand, interrupt_check=lambda: False, sleep_time=0.03)
            detector.terminate()
            
            if self.use_voice_input: 
                wake_command = self.takecommand()
               
                if wake_command in ["切换文字输入", "1"]:
                    self.use_voice_input = False
                    print("已切换到文字手写输入模式")
                elif self.WAKE_WORD in wake_command or wake_command.startswith("打开"):
                    print("已唤醒，等待命令...")
                    self.logging.info("已唤醒，等待命令")
                    time.sleep(1)

                    command = wake_command.replace(self.WAKE_WORD, '').strip() if self.WAKE_WORD in wake_command else wake_command
                    self.handle_user_command(command, handler, programs)
                else:
                    self.match_and_run_program(wake_command, programs, self.program_folder)
            else:
                user_input = self.process_text_input()
                self.handle_user_command(user_input, handler, programs)

        observer.stop()
        observer.join()
        if not self.running:
            os.system("python Bide_one's_time.py")
                
        root = tk.Tk()
        root.title("jarvis交互面板")
        root.geometry("800x600")

        panel = CommandPanel(root, [])
        panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        root.mainloop()

    class ProgramHandler(FileSystemEventHandler):
        def __init__(self, program_folder, external_folders=None):
            self.program_folder = program_folder
            self.external_folders = external_folders or []
            self.programs_cache = {}
            self.programs = self.open_programs()

        def on_modified(self, event):
            if event.src_path.endswith('.py') or event.src_path.split('.')[-1] in binary_extensions:
                self.programs = self.open_programs.clear_cache()()

        def on_created(self, event):
            if event.src_path.endswith('.py') or event.src_path.split('.')[-1] in binary_extensions:
                self.programs = self.open_programs.clear_cache()()

        @lru_cache(maxsize=128)
        def open_programs(self):
            return Jarvis().open_programs(self.program_folder, self.external_folders)

if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.main()
