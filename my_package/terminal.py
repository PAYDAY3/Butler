import os
import shutil
import subprocess
import paramiko
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, simpledialog, messagebox
from concurrent.futures import ThreadPoolExecutor
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from tkinter import simpledialog
from tkinter import filedialog

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self.history = []
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.commands = ['cd', 'ls', 'mkdir', 'rmdir', 'cp', 'mv', 'git']
        self.session = PromptSession(completer=WordCompleter(self.commands))
        
    def create_widgets(self):
        # 创建输入框和按钮
        self.input = tk.Entry(self)
        self.input.pack(side="left", fill=tk.X, padx=5, pady=5)
        self.run_button = tk.Button(self, text="Run", command=self.execute_command)
        self.run_button.pack(side="left", padx=5, pady=5))

        # 创建文本框
        self.result_text = tk.Text(self, height=10, width=50)
        self.result_text.pack(side="bottom")
        self.result_text.config(state=tk.DISABLED)
        
        # 创建菜单栏
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Exit", command=self.master.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open File", command=self.open_file)
        self.file_menu.add_command(label="Open Folder", command=self.open_folder) 
  
        # 创建历史记录菜单
        self.history_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.history_menu.add_command(label="Show History", command=self.show_history)
        self.menu_bar.add_cascade(label="History", menu=self.history_menu)
        
        # SSH菜单
        self.ssh_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.ssh_menu.add_command(label="连接SSH", command=self.connect_ssh)
        self.ssh_menu.add_command(label="断开SSH", command=self.disconnect_ssh)
        self.menu_bar.add_cascade(label="SSH", menu=self.ssh_menu)     
      def connect_ssh(self):
        host = simpledialog.askstring("SSH主机", "输入SSH主机:")
        port = simpledialog.askinteger("SSH端口", "输入SSH端口:", initialvalue=22)
        username = simpledialog.askstring("SSH的用户名", "输入SSH用户名:")
        password = simpledialog.askstring("SSH密码", "输入SSH密码:", show='*')
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh_client.connect(host, port, username, password)
            self.update_result_text("Connected to SSH server.")    
        except paramiko.AuthenticationException:
            self.update_result_text("Authentication failed.")
        except paramiko.SSHException as sshException:
            self.update_result_text(f"Unable to establish SSH connection: {sshException}")
        except Exception as e:
            self.update_result_text(f"Exception in connecting to SSH server: {e}")

    def disconnect_ssh(self):
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            self.update_result_text("与SSH服务器断开连接")
            
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.update_result_text(f"选定的文件: {file_path}")

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.update_result_text(f"所选文件夹: {folder_path}")      
 
    def execute_command(self):
        command = self.input.get()
        self.history.append(command)
        self.executor.submit(self.execute_command_in_thread, command)
        if self.ssh_client:
            self.executor.submit(self.execute_remote_command, command)
        else:
            self.executor.submit(self.execute_local_command, command)
    
    def execute_command_in_thread(self, command):
        try:
            if command.startswith('cd '):
                path = command.split(' ', 1)[1]
                os.chdir(path)
                self.update_result_text(f"已更改目录为: {os.getcwd()}")
            elif command == 'ls':
                files = os.listdir(os.getcwd())
                self.update_result_text('\n'.join(files))
            else:
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
                self.update_result_text(text=f"将当前目录更改为: {os.getcwd()}")
            else:
                self.update_result_text(text=f"将当前目录更改为: {os.getcwd()}")
                
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
        
def show_history(self):
    history_str = "\n".join(self.history)
    simpledialog.messagebox.showinfo("命令历史记录", history_str)        

def terminal():
    # 创建图形界面应用程序
    root = tk.Tk()
    app = Application(master=root)
    app.pack(fill=tk.BOTH, expand=True)

    # 运行命令行交互程序
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

    # 启动图形界面应用程序
    app.mainloop()

if __name__ == '__main__':
    terminal()
