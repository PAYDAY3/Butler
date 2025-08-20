import os
import sys
import time
import importlib
import importlib.util
import pyttsx3
import datetime
import subprocess
import tkinter as tk
from tkinter import messagebox
from pydub import AudioSegment
from pydub.playback import play
import requests
import shutil
import tempfile
import concurrent.futures
from functools import lru_cache
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import numpy as np
import heapq
import math
import cv2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 假设这些模块存在
from package.thread import process_tasks
from . import binary_extensions
from package.virtual_keyboard import VirtualKeyboard
from package import Logging
from butler.CommandPanel import CommandPanel
from plugin.plugin import process_command as process_plugin_command

class Jarvis:
    def __init__(self, root):
        self.root = root
        load_dotenv()
        # 替换为DeepSeek API密钥
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.engine = pyttsx3.init()
        self.logging = Logging.get_logger(__name__)

        base_dir = os.path.dirname(__file__)
        self.JARVIS_AUDIO_FILE = os.path.join(base_dir, "resources", "jarvis.wav")

        # Paths for temporary files are relative to the current working directory
        self.OUTPUT_FILE = "./temp.wav"

        self.program_mapping = {
            "邮箱": "e-mail.py",
            "播放音乐": "music.py",
            "虚拟键盘": "virtual_keyboapy.py",
            "组织文件": "Organizepy.py",
            "爬虫": "crawlpy.py",
            "终端": "terminpy.py",
            "加密": "encrypt.py",
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
        self.matched_program = None
        self.panel = None

    def set_panel(self, panel):
        self.panel = panel

    def ui_print(self, message):
        print(message)
        if self.panel:
            self.panel.append_to_history(message)

    # 1.算法实现部分
    def quick_sort(self, arr):
        """快速排序算法"""
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return self.quick_sort(left) + middle + self.quick_sort(right)
    
    def merge_sort(self, arr):
        """归并排序算法"""
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = arr[:mid]
        right = arr[mid:]
        
        left = self.merge_sort(left)
        right = self.merge_sort(right)
        
        return self.merge(left, right)
    
    def merge(self, left, right):
        """归并排序的合并操作"""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    # 2. 搜索算法
    def binary_search(self, arr, target):
        """二分查找算法"""
        low, high = 0, len(arr) - 1
        
        while low <= high:
            mid = (low + high) // 2
            mid_val = arr[mid]
            
            if mid_val == target:
                return mid
            elif mid_val < target:
                low = mid + 1
            else:
                high = mid - 1
        
        return -1
    
    # 3. 路径规划算法
    def dijkstra(self, graph, start):
        """Dijkstra最短路径算法"""
        distances = {node: float('infinity') for node in graph}
        distances[start] = 0
        priority_queue = [(0, start)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            if current_distance > distances[current_node]:
                continue
                
            for neighbor, weight in graph[current_node].items():
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        return distances
    
    # 4. 文本相似度算法
    def cosine_similarity(self, text1, text2):
        """计算两个文本的余弦相似度"""
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity[0][0]
    
    # 5. 图像处理算法
    def edge_detection(self, image_path):
        """边缘检测算法"""
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return None
            
        # 应用Canny边缘检测
        edges = cv2.Canny(image, 100, 200)
        return edges
    
    # 6. 数学算法
    def fibonacci(self, n):
        """计算斐波那契数列第n项"""
        if n <= 0:
            return 0
        elif n == 1:
            return 1
            
        a, b = 0, 1
        for _ in range(2, n+1):
            a, b = b, a + b
        return b
    
    # 核心功能
    def preprocess(self, text):
        # 使用DeepSeek API
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个AI助手，负责文本预处理。"},
                {"role": "user", "content": text}
            ],
            "max_tokens": 512,
            "temperature": 0
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            self.ui_print(f"DeepSeek API调用失败: {e}")
            return text  # 出错时返回原始文本

    def generate_response(self, text):
        # 使用DeepSeek API
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个AI助手，负责生成自然语言响应。"},
                {"role": "user", "content": text}
            ],
            "max_tokens": 150,
            "temperature": 0.5
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            self.ui_print(f"DeepSeek API调用失败: {e}")
            return "抱歉，我暂时无法回答这个问题。"  # 出错时返回默认响应

    def speak(self, audio):
        self.ui_print(f"Jarvis: {audio}")
        # 保存临时语音文件
        self.engine.save_to_file(audio, self.OUTPUT_FILE)
        self.engine.runAndWait()
        
        try:
            # 直接播放合成语音
            sound = AudioSegment.from_wav(self.OUTPUT_FILE)
            play(sound)
        except Exception as e:
            self.ui_print(f"音频处理出错: {e}")
        finally:
            # 清理临时文件
            if os.path.exists(self.OUTPUT_FILE):
                os.remove(self.OUTPUT_FILE)

    def takecommand(self):
        speech_key = os.getenv("AZURE_SPEECH_KEY")
        service_region = os.getenv("AZURE_SERVICE_REGION", "chinaeast2")
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_language = "zh-CN"
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

        self.ui_print("请说话...")

        try:
            result = recognizer.recognize_once()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                query = result.text
                self.ui_print('User: ' + query + '\n')
                return query
            elif result.reason == speechsdk.ResultReason.NoMatch:
                self.ui_print("对不起，我没有听清楚，请再说一遍。")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                self.ui_print(f"语音识别取消: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    self.ui_print(f"错误详情: {cancellation_details.error_details}")
                return None

        except Exception as e:
            self.ui_print(f"语音识别出错: {e}")
            self.logging.error(f"语音识别出错: {e}")
            return None

    def handle_user_command(self, command, programs):
        if command is None:
            return
            
        # 处理算法相关命令
        if command.startswith("排序数字"):
            try:
                numbers = [int(n) for n in command[4:].split()]
                sorted_nums = self.quick_sort(numbers)
                self.speak(f"排序结果: {sorted_nums}")
                return
            except Exception as e:
                self.speak("排序失败，请确保输入的是数字")
                return
                
        if command.startswith("查找数字"):
            try:
                parts = command[4:].split()
                target = int(parts[-1])
                arr = [int(n) for n in parts[:-1]]
                arr.sort()
                index = self.binary_search(arr, target)
                if index != -1:
                    self.speak(f"数字 {target} 在排序后的位置是: {index}")
                else:
                    self.speak(f"数字 {target} 不在数组中")
                return
            except Exception as e:
                self.speak("查找失败，请确保输入格式正确")
                return
                
        if command.startswith("计算斐波那契"):
            try:
                n = int(command[6:].strip())
                fib = self.fibonacci(n)
                self.speak(f"斐波那契数列第{n}项是: {fib}")
                return
            except Exception as e:
                self.speak("计算失败，请输入有效的数字")
                return
                
        if command.startswith("检测图像边缘"):
            try:
                image_path = command[6:].strip()
                if os.path.exists(image_path):
                    edges = self.edge_detection(image_path)
                    if edges is not None:
                        output_path = os.path.splitext(image_path)[0] + '_edges.jpg'
                        cv2.imwrite(output_path, edges)
                        self.speak(f"边缘检测完成，结果已保存到: {output_path}")
                    else:
                        self.speak("图像处理失败")
                else:
                    self.speak("找不到指定的图像文件")
                return
            except Exception as e:
                self.speak("图像处理出错")
                return
                
        if command.startswith("计算文本相似度"):
            try:
                parts = command[7:].split("和")
                if len(parts) == 2:
                    text1 = parts[0].strip()
                    text2 = parts[1].strip()
                    similarity = self.cosine_similarity(text1, text2)
                    self.speak(f"文本相似度是: {similarity:.2f}")
                else:
                    self.speak("请提供两段文本，用'和'分隔")
                return
            except Exception as e:
                self.speak("相似度计算失败")
                return
            
        # 处理普通命令
        if command.startswith("打开"):
            program_name = command[3:].strip()
            if program_name in self.program_mapping:
                self.execute_program(self.program_mapping[program_name])
            else:
                self.ui_print(f"未找到程序 '{program_name}'")
                self.speak(f"未找到程序 {program_name}")
        elif command in self.program_mapping:
            self.execute_program(self.program_mapping[command])
        elif command.startswith(("进行", "运行")):
            program_name = command[2:].strip()
            if program_name in programs:
                self.execute_program(programs[program_name])
            else:
                self.ui_print(f"未找到程序 '{program_name}'")
                self.speak(f"未找到程序 {program_name}")
        elif "退出" in command or "结束" in command:
            self.logging.info(f"程序已退出")
            self.speak(f"程序已退出")
            self.running = False
            self.root.quit()
        else:
            plugin_result = process_plugin_command(command)
            if "未找到匹配的插件" not in plugin_result:
                self.speak(plugin_result)
            else:
                self.ui_print("未知指令，请重试")
                self.logging.warning("未知指令")
                self.speak("未识别到有效指令")
                time.sleep(1)
                self.match_program(command, programs)

    @lru_cache(maxsize=128)
    def open_programs(self, program_folder, external_folders=None):
        programs_cache = {}
        all_folders = [program_folder] + (external_folders or [])
        
        for folder in all_folders:
            if not os.path.exists(folder):
                self.ui_print(f"文件夹 '{folder}' 未找到。")
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
                                self.ui_print(f"加载程序模块 '{program_name}' 时出错：{e}")
                                self.logging.info(f"加载程序模块 '{program_name}' 时出错：{e}")
                                continue

                            if not hasattr(program_module, 'run'):
                                self.ui_print(f"程序模块 '{program_name}' 无效。")
                                self.logging.info(f"程序模块 '{program_name}' 无效。")
                                continue

                        programs[program_name] = program_module
                    
        programs = dict(sorted(programs.items()))
        return programs
    
    def execute_program(self, program_name):
        try:
            # 尝试从缓存中获取模块
            if program_name in sys.modules:
                program_module = sys.modules[program_name]
            else:
                # 查找文件路径
                program_path = None
                for folder in self.program_folder:
                    for root, dirs, files in os.walk(folder):
                        if program_name in files:
                            program_path = os.path.join(root, program_name)
                            break
                    if program_path:
                        break
                
                if not program_path:
                    self.ui_print(f"未找到程序文件: {program_name}")
                    self.speak(f"未找到程序 {program_name}")
                    return
                
                # 动态加载模块
                spec = importlib.util.spec_from_file_location(program_name, program_path)
                program_module = importlib.util.module_from_spec(spec)
                sys.modules[program_name] = program_module
                spec.loader.exec_module(program_module)
            
            # 执行程序
            if hasattr(program_module, 'run'):
                self.ui_print(f"执行程序: {program_name}")
                self.speak(f"正在启动 {program_name}")
                program_module.run()
            else:
                self.ui_print(f"程序 {program_name} 没有run方法")
                self.speak(f"程序 {program_name} 无法启动")
                
        except Exception as e:
            self.ui_print(f"执行程序出错: {e}")
            self.logging.error(f"执行程序 {program_name} 出错: {e}")
            self.speak(f"启动程序时出错")

    def manage_temp_files(self):
        """管理临时文件"""
        temp_dir = tempfile.gettempdir()
        for filename in os.listdir(temp_dir):
            if filename.startswith("jarvis_temp_"):
                filepath = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                except Exception as e:
                    self.ui_print(f"删除临时文件失败: {filepath} - {e}")

    def match_program(self, command, programs):
        """尝试匹配程序"""
        # 简化实现 - 实际应用中应使用更智能的匹配
        for name in programs:
            if name in command:
                self.execute_program(name)
                return
        self.speak("未找到匹配的程序")

    def panel_command_handler(self, command_type, command_payload):
        programs = self.open_programs(["./program"])
        if command_type == "text":
            self.ui_print(f"User: {command_payload}")
            self.handle_user_command(command_payload, programs)
        elif command_type == "voice":
            command = self.takecommand()
            if command:
                self.handle_user_command(command, programs)

    def main(self):
        # handler = self.ProgramHandler(self.program_folder)
        # observer = Observer()
        # for folder in self.program_folder:
        #     observer.schedule(handler, folder, recursive=True)
        # observer.start()

        process_tasks()
        # schedule_management() # This is a standalone command line tool, disabling for now
        self.manage_temp_files()

        self.speak("Jarvis 助手已启动")
        
        # observer.stop()
        # observer.join()

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
            return Jarvis(None).open_programs(self.program_folder, self.external_folders)

def main():
    """Main entry point for the application."""
    try:
        root = tk.Tk()
        root.title("Jarvis Assistant")
        root.geometry("800x600")

        jarvis = Jarvis(root)

        panel = CommandPanel(root)
        panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        panel.set_command_callback(jarvis.panel_command_handler)
        jarvis.set_panel(panel)

        jarvis.main()

        root.mainloop()

    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")

if __name__ == "__main__":
    main()
