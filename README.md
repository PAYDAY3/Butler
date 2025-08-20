Jarvis - 智能语音助手系统

项目概述

Jarvis 是一个功能丰富的智能语音助手系统，基于 Python 开发，集成了语音识别、自然语言处理、多种算法实现和程序管理功能。该系统采用模块化设计，支持插件扩展，能够通过语音或文本指令执行各种复杂任务。

系统架构

核心组件

· 语音处理模块: 集成 Azure 语音服务
· 自然语言处理: 使用 DeepSeek API 进行文本理解和生成
· 程序管理: 动态加载和执行外部程序模块
· 算法库: 内置多种常用算法实现
· GUI 界面: 基于 Tkinter 的交互面板
· 文件监控: 使用 Watchdog 实现文件系统实时监控

功能详细说明

1. 语音交互系统

语音识别

```python
# 使用 Azure 语音服务进行语音识别
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_language = "zh-CN"
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
```

语音合成

```python
# 使用 pyttsx3 进行语音合成，支持音效混合
engine = pyttsx3.init()
engine.save_to_file(audio, self.OUTPUT_FILE)
```

2. 算法实现库

排序算法

```python
def quick_sort(self, arr):
    """快速排序算法实现"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return self.quick_sort(left) + middle + self.quick_sort(right)

def merge_sort(self, arr):
    """归并排序算法实现"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]
    
    left = self.merge_sort(left)
    right = self.merge_sort(right)
    
    return self.merge(left, right)
```

搜索算法

```python
def binary_search(self, arr, target):
    """二分查找算法实现"""
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
```

图算法

```python
def dijkstra(self, graph, start):
    """Dijkstra 最短路径算法实现"""
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
```

文本处理算法

```python
def cosine_similarity(self, text1, text2):
    """计算文本余弦相似度"""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]
```

图像处理算法

```python
def edge_detection(self, image_path):
    """Canny 边缘检测算法"""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return None
        
    # 应用 Canny 边缘检测
    edges = cv2.Canny(image, 100, 200)
    return edges
```

数学算法

```python
def fibonacci(self, n):
    """计算斐波那契数列"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
        
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b
```

3. 程序管理系统

程序映射表

```python
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
    "文本编辑器": self.edit_tool,
    "终端命令": self.bash_tool,
    "计算机控制": self.computer_tool
}
```

动态程序加载

```python
@lru_cache(maxsize=128)
def open_programs(self, program_folder, external_folders=None):
    """动态加载程序模块"""
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
```

4. 文件系统监控

```python
class ProgramHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    def __init__(self, program_folder, external_folders=None):
        self.program_folder = program_folder
        self.external_folders = external_folders or []
        self.programs_cache = {}
        self.programs = self.open_programs()

    def on_modified(self, event):
        """文件修改事件处理"""
        if event.src_path.endswith('.py') or event.src_path.split('.')[-1] in binary_extensions:
            self.programs = self.open_programs.clear_cache()()

    def on_created(self, event):
        """文件创建事件处理"""
        if event.src_path.endswith('.py') or event.src_path.split('.')[-1] in binary_extensions:
            self.programs = self.open_programs.clear_cache()()

    @lru_cache(maxsize=128)
    def open_programs(self):
        """打开程序文件"""
        return Jarvis().open_programs(self.program_folder, self.external_folders)
```

安装和配置

系统要求

· Python 3.7+
· Windows/Linux/macOS
· 麦克风设备（语音功能）
· 音频输出设备

依赖安装

```bash
# 核心依赖
pip install pyttsx3 pydub requests

# 语音识别
pip install azure-cognitiveservices-speech

# 文件监控
pip install watchdog

# 图像处理
pip install opencv-python

# 文本处理
pip install scikit-learn

# 数学计算
pip install numpy
```

API 密钥配置

1. DeepSeek API 配置
   ```python
   # 在 jarvis.py 中设置
   self.deepseek_api_key = "您的 DeepSeek API 密钥"
   ```
2. Azure 语音服务配置
   ```python
   # 在 jarvis.py 中设置
   speech_key = "您的 Azure 语音服务密钥"
   service_region = "您的服务区域"
   ```

使用指南

启动系统

```bash
python jarvis.py
```

语音指令格式

基本指令

· "打开 [程序名]" - 启动程序
· "运行 [程序名]" - 运行程序
· "切换文字输入" - 切换到文本模式
· "退出"/"结束" - 退出系统

算法指令示例

1. 数字排序
   ```
   排序数字 5 3 8 1 9
   ```
2. 数字查找
   ```
   查找数字 3 1 4 2 5
   ```
3. 斐波那契计算
   ```
   计算斐波那契 10
   ```
4. 图像处理
   ```
   检测图像边缘 /path/to/image.jpg
   ```
5. 文本相似度
   ```
   计算文本相似度 你好世界 和 世界你好
   ```

文本输入模式

在语音模式下说"切换文字输入"或"1"可切换到文本输入模式，此时会弹出图形界面供用户输入文本指令。

程序管理

系统会自动扫描 program_folder 中定义的程序目录，加载所有有效的 Python 程序文件。有效的程序文件必须：

1. 具有 .py 扩展名或以 invoke.py 结尾
2. 包含 run() 方法
3. 位于指定的程序目录中

目录结构

```
jarvis/
├── jarvis.py                 # 主程序文件
├── program/                  # 程序目录
│   ├── e-mail.py            # 邮箱程序
│   ├── music.py             # 音乐播放程序
│   ├── virtual_keyboapy.py  # 虚拟键盘程序
│   └── ...                  # 其他程序
├── package/                  # 自定义包
│   ├── __init__.py
│   ├── thread.py            # 多线程处理
│   ├── TextEditor.py        # 文本编辑器
│   ├── virtual_keyboard.py  # 虚拟键盘
│   ├── Logging.py           # 日志管理
│   └── schedule_management.py # 日程管理
├── plugin/                   # 插件目录
│   ├── __init__.py
│   └── plugin.py            # 插件系统
├── temp.wav                 # 临时音频文件（运行时生成）
└── final_output.wav         # 最终输出音频文件（运行时生成）
```

故障排除

常见问题

1. 语音识别失败
   · 检查 Azure 语音服务密钥配置
   · 确认网络连接正常
2. 程序加载失败
   · 确认程序目录结构正确
   · 检查程序文件是否有 run() 方法
4. 音频播放问题
   · 检查音频输出设备
   · 确认 pydub 依赖已正确安装

日志记录

系统使用内置的日志记录功能，可以通过查看日志来诊断问题：

```python
self.logging.info("信息日志")
self.logging.warning("警告日志")
self.logging.error("错误日志")
```

扩展开发

添加新程序

1. 在 program/ 目录下创建新的 Python 文件
2. 实现 run() 方法作为程序入口
3. 在 program_mapping 中添加程序映射

添加新算法

1. 在 Jarvis 类中添加新的算法方法
2. 在 handle_user_command 方法中添加对应的指令处理逻辑
3. 更新使用文档

插件开发

系统支持插件扩展，可以在 plugin/ 目录下开发新的插件模块。

性能优化

1. 缓存机制: 使用 lru_cache 缓存程序加载结果
2. 并发处理: 使用线程池处理并发任务
3. 资源管理: 自动清理临时文件，避免资源泄漏

安全考虑

1. API 密钥保护: 不要将 API 密钥硬编码在代码中，建议使用环境变量
2. 程序执行安全: 动态加载的程序应来自可信来源
3. 文件访问权限: 限制程序对系统文件的访问权限

许可证

本项目采用 MIT 许可证。详情请参阅项目根目录下的 LICENSE 文件。

贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目。贡献时请确保：

1. 代码符合 PEP 8 规范
2. 添加适当的测试用例
3. 更新相关文档
4. 遵循项目的代码风格

技术支持

如有问题或需要技术支持，请通过以下方式联系：

· 提交 GitHub Issue
· 查看项目文档
· 参考示例代码

---

注意：本项目仍在积极开发中，API 和功能可能会有变动。建议定期查看更新日志以获取最新信息。
