import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor
from prompt_toolkit import PromptSession

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.executor = ThreadPoolExecutor(max_workers=5)

    def create_widgets(self):
        # 创建输入框和按钮
        self.input = tk.Entry(self)
        self.input.pack(side="left")
        self.run_button = tk.Button(self, text="Run", command=self.execute_command)
        self.run_button.pack(side="left")

        # 创建文本框
        self.result_text = tk.Text(self, height=10, width=50)
        self.result_text.pack(side="bottom")
        self.result_text.config(state=tk.DISABLED)

    def execute_command(self):
        command = self.input.get()
        self.executor.submit(self.execute_command_in_thread, command)

    def execute_command_in_thread(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout.strip()
            error = result.stderr.strip()
            self.update_result_text(f"{output}\n{error}")
        except subprocess.CalledProcessError as e:
            self.update_result_text(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}")
        except subprocess.TimeoutExpired as e:
            self.update_result_text(f"Command '{e.cmd}' timed out after {e.timeout} seconds")
        except Exception as e:
            self.update_result_text(f"Error executing command: {e}")

    def update_result_text(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, text + '\n')
        self.result_text.config(state=tk.DISABLED)

def execute_command(command):
    command_parts = command.split()
    if not command_parts:
        return

    cmd = command_parts[0]
    args = command_parts[1:]

    try:
        if cmd == 'cd':
            if args:
                os.chdir(args[0])
                print(f"Changed current directory to: {os.getcwd()}")
            else:
                print("No directory specified.")
        elif cmd == 'ls':
            files = os.listdir(os.getcwd())
            for file in files:
                print(file)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout.strip()
            if output:
                print(output)
            error = result.stderr.strip()
            if error:
                print(error)
    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}")
    except subprocess.TimeoutExpired as e:
        print(f"Command '{e.cmd}' timed out after {e.timeout} seconds")
    except Exception as e:
        print(f"Error executing command: {e}")

def execute_script(script_file):
    try:
        with open(script_file) as file:
            script = file.read()
            execute_command(script)
    except FileNotFoundError:
        print(f"Script file '{script_file}' not found.")
    except Exception as e:
        print(f"Error executing script: {e}")


def main():
    session = PromptSession()

    while True:
        try:
            user_input = session.prompt(">>> ")
            if user_input.lower() == 'exit':
                break
            else:
                execute_command(user_input)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == '__main__':
    # 创建图形界面应用程序
    root = tk.Tk()
    app = Application(master=root)

    # 运行命令行交互程序
    main()

    # 启动图形界面应用程序
    app.mainloop()

    
    
    
