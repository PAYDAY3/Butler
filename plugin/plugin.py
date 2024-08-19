import tkinter as tk
from tkinter import messagebox
from my_package import Logging
from plugin_manager import PluginManager
from jarvis.jarvis import takecommand, speak
from jarvis.CommandPanel import CommandPanel
from jarvis import InputProcessor

# 配置日志
logger = Logging.getLogger(__name__)

# 初始化 PluginManager 并传入插件包的路径
plugin_manager = PluginManager(plugin_package="plugins")

# 插件名称列表
plugins_to_manage = {
    "TimePlugin": {
        "takecommand": "查询时间",
        "args": {}
    },
    "CountdownPlugin": {
        "takecommand": "倒计时",
        "args": {}
    },
    "FileSearchPlugin": {
        "takecommand": ["搜索", "搜索一下"], # 文件搜索
        "args": {}
    },
    "JokePlugin": {
        "takecommand": ["我无聊了", "休息一下", "讲个笑话", "好无聊"],  # 触发命令
        "args": {}  # 没有需要的参数
    },
    "NLPPlugin": {
        "takecommand": ["执行 NLP 任务", "处理文本"],
        "args": {}
    },
    "NotepadPlugin": {
        "takecommand": ["记笔记", "添加笔记"],
        "args": {}
    },
    "TodoPlugin": {
        "takecommand": {"添加待办事项", "列出待办事项", "删除待办事项"},
        "args": {}
    },
    "clear_recent_memory": {
        "takecommand": {"清理长期记忆"},
        "args": {}
    },
    "downloaded_url": {
        "takecommand": {"下载网页"},
        "args": {}
    },
    "read_file": {
        "takecommand": {"读取", "读取文件"},
        "args": {}
    },
    "write_file": {
        "takecommand": {"写入", "写入文件"},
        "args": {}
    },
}

# 加载所有插件
all_plugins = plugin_manager.get_all_plugins()
logger.info(f"已加载插件: {[plugin.get_name() for plugin in all_plugins]}")

def match_command_to_plugin(command: str):
    """根据语音命令匹配对应的插件."""
    for plugin_name, details in plugins_to_manage.items():
        takecommands = details['takecommand']
        
        # 如果 takecommands 是字符串，将其转换为列表
        if isinstance(takecommands, str):
            takecommands = [takecommands]
        
        # 检查命令是否匹配任何一个指定的触发命令
        if any(cmd in command for cmd in takecommands):
            return plugin_name, details['args']
    return None, None

def process_command(command: str):
    """处理指令并执行相应的插件."""
    plugin_name, args = match_command_to_plugin(command)

    if plugin_name:
        logger.info(f"匹配到插件: {plugin_name}，执行中...")
        result = plugin_manager.run_plugin(name=plugin_name, takecommand=command, args=args)
        logger.info(f"{plugin_name} 运行结果: {result}")
        speak(f"{plugin_name} 运行结果: {result}")
        
        # 获取插件状态
        status = plugin_manager.get_plugin_status(name=plugin_name)
        logger.info(f"{plugin_name} 状态: {status}")
        speak(f"{plugin_name} 状态: {status}")

        # 停止插件
        stop_result = plugin_manager.stop_plugin(name=plugin_name)
        logger.info(f"{plugin_name} 停止结果: {stop_result}")
        speak(f"{plugin_name} 停止结果: {stop_result}")
    else:
        speak("未找到匹配的插件。请尝试其他命令。")
        
def plugin():
    """主函数，处理语音和文字输入，默认语音输入。"""
    use_text_input = False  # 默认使用语音输入
    input_processor = InputProcessor.InputProcessor()
    while True:
        if not use_text_input:
            # 语音输入模式
            command = input_processor.process_voice_input()

            if not command:
                speak("请再说一遍，我没有听清楚。")
                continue

        else:
            # 文字输入模式
            command = input_processor.process_text_input()  # input("请输入命令：")

        # 处理命令
        process_command(command)

        if not use_text_input:
            # 切换到文字输入
            switch_input = input("输入 1 切换到文字输入，输入 2 返回语音输入，其他键退出：")
            if switch_input == "1":
                use_text_input = True
                speak("已切换到文字输入模式。")
            elif switch_input == "2":
                use_text_input = False
                speak("已切换到语音输入模式。")
            else:
                speak("退出程序。")
                break
        else:
            # 切换到语音输入
            switch_input = input("输入 2 返回语音输入，其他键退出：")
            if switch_input == "2":
                use_text_input = False
                speak("已切换到语音输入模式。")
            else:
                speak("退出程序。")
                break    
                                    
# 创建主窗口
root = tk.Tk()
root.title("Jarvis 交互面板")
root.geometry("800x600")

# 创建交互式命令行面板
panel = CommandPanel(root, [])
panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# 启动插件功能的线程
import threading
plugin_thread = threading.Thread(target=plugin)
plugin_thread.start()

# 启动主事件循环
root.mainloop()
        
