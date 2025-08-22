import os
import sys
import time
import importlib
import importlib.util
import pyttsx3
import datetime
import subprocess
import json
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
from package.log_manager import LogManager
from butler.CommandPanel import CommandPanel
from plugin.PluginManager import PluginManager

class Jarvis:
    def __init__(self, root):
        self.root = root
        load_dotenv()
        # 替换为DeepSeek API密钥
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.engine = pyttsx3.init()
        self.logging = LogManager.get_logger(__name__)
        self.plugin_manager = PluginManager("plugin")

        base_dir = os.path.dirname(__file__)
        self.JARVIS_AUDIO_FILE = os.path.join(base_dir, "resources", "jarvis.wav")

        # Load prompts from the JSON file
        try:
            prompts_path = os.path.join(base_dir, "prompts.json")
            with open(prompts_path, 'r', encoding='utf-8') as f:
                self.prompts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logging.error(f"Failed to load prompts: {e}")
            # Fallback to empty prompts if loading fails
            self.prompts = {}

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
        self.MAX_HISTORY_MESSAGES = 10

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
        """
        使用DeepSeek API将用户输入文本转换为结构化的意图和实体。
        """
        # 从加载的配置中获取系统提示
        system_prompt = self.prompts.get("nlu_intent_extraction", {}).get("prompt")
        if not system_prompt:
            self.logging.error("NLU intent extraction prompt not found. Using fallback.")
            # Provide a minimal fallback prompt to avoid crashing
            system_prompt = "You are an NLU assistant. Return JSON with 'intent' and 'entities'."

        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        # 构造发送给API的消息列表
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history)

        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result_text = response.json()['choices'][0]['message']['content']

            # 清理和解析JSON
            # LLM有时会返回被markdown代码块包围的JSON
            if result_text.strip().startswith("```json"):
                result_text = result_text.strip()[7:-4].strip()

            return json.loads(result_text)
        except requests.exceptions.RequestException as e:
            self.ui_print(f"DeepSeek API 请求失败: {e}")
            return {"intent": "unknown", "entities": {"error": str(e)}}
        except json.JSONDecodeError as e:
            self.ui_print(f"无法解析来自API的JSON响应: {e}")
            self.logging.error(f"原始响应文本: {result_text}")
            return {"intent": "unknown", "entities": {"error": "Invalid JSON response"}}
        except (KeyError, IndexError) as e:
            self.ui_print(f"API响应格式不符合预期: {e}")
            return {"intent": "unknown", "entities": {"error": "Unexpected API response format"}}

    def generate_response(self, text):
        # 使用DeepSeek API
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        # 从加载的配置中获取系统提示
        system_prompt = self.prompts.get("general_response", {}).get("prompt")
        if not system_prompt:
            self.logging.error("General response prompt not found. Using fallback.")
            system_prompt = "You are a helpful AI assistant."

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
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

        # 将助手的响应添加到历史记录
        self.conversation_history.append({"role": "assistant", "content": audio})
        # 裁剪历史记录，防止其无限增长
        if len(self.conversation_history) > self.MAX_HISTORY_MESSAGES:
            self.conversation_history = self.conversation_history[-self.MAX_HISTORY_MESSAGES:]

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

        # 将用户的命令添加到历史记录
        self.conversation_history.append({"role": "user", "content": command})

        nlu_result = self.preprocess(command)
        intent = nlu_result.get("intent", "unknown")
        entities = nlu_result.get("entities", {})

        intent_handlers = {
            "sort_numbers": self._handle_sort_numbers,
            "find_number": self._handle_find_number,
            "calculate_fibonacci": self._handle_calculate_fibonacci,
            "edge_detect_image": self._handle_edge_detect_image,
            "text_similarity": self._handle_text_similarity,
            "open_program": self._handle_open_program,
            "exit": self._handle_exit,
        }

        handler = intent_handlers.get(intent)

        if handler:
            handler(entities=entities, programs=programs)
        else:
            # Fallback to plugin or unknown command
            plugin_found = False
            for plugin in self.plugin_manager.get_all_plugins():
                if plugin.get_name().lower() in command.lower():
                    plugin_result = self.plugin_manager.run_plugin(plugin.get_name(), command, entities)
                    if plugin_result.success:
                        self.speak(plugin_result.result)
                        plugin_found = True
                        break

            if not plugin_found:
                self.ui_print(f"未知指令或意图: {command}")
                self.logging.warning(f"未知指令或意图: {intent}")
                self.speak("抱歉，我不太理解您的意思，请换一种方式表达。")

    def _handle_sort_numbers(self, entities, **kwargs):
        try:
            numbers = entities.get("numbers", [])
            if not numbers or not all(isinstance(n, (int, float)) for n in numbers):
                 self.speak("排序失败，请提供有效的数字列表。")
                 return
            sorted_nums = self.quick_sort(numbers)
            self.speak(f"排序结果: {sorted_nums}")
        except Exception as e:
            self.speak(f"排序时发生错误: {e}")

    def _handle_find_number(self, entities, **kwargs):
        try:
            numbers = entities.get("numbers", [])
            target = entities.get("target")
            if not numbers or target is None:
                self.speak("查找失败，请提供数字列表和目标数字。")
                return

            numbers.sort()
            index = self.binary_search(numbers, target)
            if index != -1:
                self.speak(f"数字 {target} 在排序后的位置是: {index}")
            else:
                self.speak(f"数字 {target} 不在数组中")
        except Exception as e:
            self.speak(f"查找时发生错误: {e}")

    def _handle_calculate_fibonacci(self, entities, **kwargs):
        try:
            n = entities.get("number")
            if n is None or not isinstance(n, int):
                self.speak("计算失败，请输入一个有效的整数。")
                return
            fib = self.fibonacci(n)
            self.speak(f"斐波那契数列第{n}项是: {fib}")
        except Exception as e:
            self.speak(f"计算斐波那契数时出错: {e}")

    def _handle_edge_detect_image(self, entities, **kwargs):
        try:
            image_path = entities.get("path")
            if not image_path or not isinstance(image_path, str):
                self.speak("图像处理失败，请提供有效的路径。")
                return

            if os.path.exists(image_path):
                edges = self.edge_detection(image_path)
                if edges is not None:
                    output_path = os.path.splitext(image_path)[0] + '_edges.jpg'
                    cv2.imwrite(output_path, edges)
                    self.speak(f"边缘检测完成，结果已保存到: {output_path}")
                else:
                    self.speak("图像处理失败，无法读取图片。")
            else:
                self.speak("找不到指定的图像文件。")
        except Exception as e:
            self.speak(f"图像处理时出错: {e}")

    def _handle_text_similarity(self, entities, **kwargs):
        try:
            text1 = entities.get("text1")
            text2 = entities.get("text2")
            if not text1 or not text2:
                self.speak("相似度计算失败，请提供两段文本。")
                return
            similarity = self.cosine_similarity(text1, text2)
            self.speak(f"文本相似度是: {similarity:.2f}")
        except Exception as e:
            self.speak(f"计算相似度时出错: {e}")

    def _handle_open_program(self, entities, programs, **kwargs):
        program_name = entities.get("program_name")
        if not program_name:
            self.speak("无法打开程序，未指定程序名称。")
            return

        # 优先匹配程序映射表
        if program_name in self.program_mapping:
            self.execute_program(self.program_mapping[program_name])
            return

        # 其次匹配动态加载的程序
        if program_name in programs:
            self.execute_program(programs[program_name])
            return

        # 最后模糊匹配
        for key in self.program_mapping:
            if program_name in key:
                self.execute_program(self.program_mapping[key])
                return

        self.ui_print(f"未找到程序 '{program_name}'")
        self.speak(f"未找到程序 {program_name}")

    def _handle_exit(self, **kwargs):
        self.logging.info("程序已退出")
        self.speak("再见")
        self.running = False
        self.root.quit()

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
        programs = self.open_programs(["./package"])
        if command_type == "text":
            self.ui_print(f"User: {command_payload}")
            self.handle_user_command(command_payload, programs)
        elif command_type == "voice":
            command = self.takecommand()
            if command and self.panel:
                self.panel.set_input_text(command)

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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", help="Run in headless mode without GUI")
    args = parser.parse_args()

    try:
        if args.headless:
            print("Running in headless mode")
            jarvis = Jarvis(None)
            jarvis.main()
            # Keep the application running for testing
            while True:
                time.sleep(1)
        else:
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
