import tkinter as tk
import subprocess
import os
from tkinter import messagebox  # 导入 messagebox

class CommandPanel(tk.Frame):
    def __init__(self, master, program_files=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.program_files = program_files or []
        # 创建面板的各个组件
        self.create_widgets()
        
        self.program_path = None
        self.panels = []  # 存储所有交互面板
        self.current_panel = self  # 当前活动的面板
        self.output_window = None
        
        # 设置面板的背景颜色为白色
        self.config(bg='white')

        self.input_frame = tk.Frame(self, bg='white')
        self.input_frame.pack(side=tk.TOP, fill=tk.X)
                
        # 添加面板按钮
        self.add_panel_button = tk.Button(self, text="+", command=self.add_panel)
        self.add_panel_button.pack(side=tk.TOP, fill=tk.X)

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(side=tk.TOP, fill=tk.X)

        # 输入框标签
        self.input_label = tk.Label(self.input_frame, text="命令：\n", bg='white')
        self.input_label.pack(side=tk.LEFT)

        # 输入框
        self.input_entry = tk.Entry(self.input_frame, bg='white', fg='black')
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.output_frame = tk.Frame(self, bg='white')
        self.output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 输出文本框
        self.output_text = tk.Text(self.output_frame, bg='white', fg='black')
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 滚动条
        self.scroll_bar = tk.Scrollbar(self.output_frame)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # 配置滚动条
        self.output_text.configure(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.configure(command=self.output_text.yview)

        # 清除按钮
        self.clear_button = tk.Button(self, text="清除", command=self.clear_output, bg='lightgray')
        self.clear_button.pack(side=tk.BOTTOM, fill=tk.X)
        self.add_button_click_effect(self.stop_button)  
        
        # 运行按钮
        self.run_button = tk.Button(self, text="运行", command=self.run_command, bg='lightgray')
        self.run_button.pack(side=tk.BOTTOM, fill=tk.X)
        self.add_button_click_effect(self.stop_button)        
        
        # "别说了" 按钮
        self.stop_button = tk.Button(self, text="别说了", command=self.stop_execution, bg='lightgray')
        self.stop_button.pack(side=tk.BOTTOM, fill=tk.X)        
        self.add_button_click_effect(self.stop_button)
        
        self.program_path = None
        self.running_process = None  # 用于存储正在运行的进程
        
    def add_panel(self):
        # 创建一个新的交互面板
        new_panel = CommandPanel(self.master, self.program_files)
        self.panels.append(new_panel)

        # 将新面板添加到 GUI 中
        new_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 设置当前活动的面板为新面板
        self.current_panel = new_panel

    def clear_output(self):
        # 清除输出文本框的内容
        if self.output_window:
            self.output_window.clear_text()


    def write_output(self, text):
        # 将文本写入输出文本框
        if not self.output_window:
            self.create_output_window()
        self.output_window.write_text(text)

    def get_input(self):
        # 获取当前面板的输入框内容
        return self.input_entry.get().strip()

    def set_input(self, text):
        # 设置当前面板的输入框内容
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, text)

    def check_and_run_command(self):
        # 获取输入的命令文本
        command = self.get_input()

        # 询问用户是否运行命令
        if command:
            response = messagebox.askyesno("确认运行", f"是否运行命令：{command}")

            # 如果用户选择运行命令，则运行命令并将其输出写入输出文本框
            if response:
                self.run_command()

    def run_command(self):
        # 获取输入的命令文本
        command = self.get_input()
        
        # 清除输出文本框
        if self.output_window is None:
            self.create_output_window()
        self.output_window.clear_text()

        # 检查第一个输入是否以 "打开" 开头
        if command.startswith("打开"):
            # 获取要打开的程序的路径
            program_path = command[3:].strip()

            # 检查程序路径是否存在
            if os.path.exists(program_path):
                # 设置程序路径
                self.program_path = program_path

                # 写入输出文本框
                self.write_output(f"已打开 {program_path}\n")
            else:
                # 写入输出文本框
                self.write_output(f"程序 {program_path} 不存在\n")
        else:
            # 如果第一个输入不是 "打开"，则将其传递给 subprocess.Popen
            try:
                # 运行命令，并捕获输出
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    self.write_output(stdout.decode() + "\n")
                else:
                    self.write_output(f"错误：{stderr.decode()}\n")
            except Exception as e:
                # 写入输出文本框
                self.write_output(f"命令执行失败：{str(e)}\n")

    def run_program(self):
        # 检查程序路径是否已设置
        if self.program_path is not None:
            # 运行程序
            subprocess.Popen([self.program_path])
        else:
            # 写入输出文本框
            self.write_output("请先打开一个程序")
            
    def auto_check_command(self):
        # 自动获取输入并询问是否运行
        self.check_and_run_command()

        # 设置定时器，1秒后再次调用
        self.after(1000, self.auto_check_command)

    def create_output_window(self):
        self.output_window = OutputWindow(self.master)
        self.output_window.protocol("WM_DELETE_WINDOW", self.on_output_window_close)

    def on_output_window_close(self):
        self.output_window.destroy()
        self.output_window = None

class OutputWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("输出窗口")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        self.output_text = tk.Text(self, bg='white', fg='black')
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_bar = tk.Scrollbar(self)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text.configure(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.configure(command=self.output_text.yview)

    def clear_text(self):
        self.output_text.delete(1.0, tk.END)

    def write_text(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        
    def add_button_click_effect(self, button):
        """
        添加按钮点击效果函数。
        """
        def on_button_click(event):
            button.config(relief=tk.SUNKEN)  # 设置按钮为凹陷状态

        def on_button_release(event):
            button.config(relief=tk.RAISED)  # 设置按钮为凸起状态

        button.bind("<Button-1>", lambda event: on_button_click(event))
        button.bind("<ButtonRelease-1>", lambda event: on_button_release(event))
        
# 创建主窗口
root = tk.Tk()
root.title("交互式命令行面板")
root.geometry("800x600")

# 创建交互式命令行面板
panel = CommandPanel(root, [])
panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# 启动主事件循环
root.mainloop()
