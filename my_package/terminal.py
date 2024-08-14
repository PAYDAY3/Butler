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
import asyncio

class SSHSession:
    def __init__(self, host, port, username, password, client, command_history=[]):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = client
        self.command_history = command_history
        self.session = PromptSession(
            completer=WordCompleter(app.commands + [PathCompleter()], ignore_case=True),
            auto_suggest=AutoSuggestFromHistory(),
            history=self.command_history,
        )

    def execute_command(self):
        command = self.session.prompt(f"{self.host}>>> ")
        self.command_history.append(command)
        self.ssh_client.exec_command(command)
        self.session.history = self.command_history
        
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
        self.ssh_sessions = {}
        self.loop = asyncio.get_event_loop()
        
    def create_widgets(self):
        # 创建输入框和按钮
        self.input = tk.Entry(self)
        self.input.pack(side="left", fill=tk.X, padx=5, pady=5)
        self.run_button = tk.Button(self, text="Run", command=self.execute_command)
        self.run_button.pack(side="left", padx=5, pady=5)

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

        # 创建脚本编辑器标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.command_frame = tk.Frame(self.notebook)
        self.notebook.add(self.command_frame, text="命令行")

        self.script_frame = tk.Frame(self.notebook)
        self.notebook.add(self.script_frame, text="脚本编辑器")

        # 命令行界面
        self.input = tk.Entry(self.command_frame)
        self.input.pack(side="left", fill=tk.X, padx=5, pady=5)
        self.run_button = tk.Button(self.command_frame, text="Run", command=self.execute_command)
        self.run_button.pack(side="left", padx=5, pady=5)

        self.result_text = tk.Text(self.command_frame, height=10, width=50)
        self.result_text.pack(side="bottom")
        self.result_text.config(state=tk.DISABLED)

        # 脚本编辑器界面
        self.script_text = scrolledtext.ScrolledText(self.script_frame, height=10, width=50)
        self.script_text.pack(fill=tk.BOTH, expand=True)
        self.run_script_button = tk.Button(self.script_frame, text="Run Script", command=self.execute_script)
        self.run_script_button.pack(pady=5)
        
        # 创建文件传输标签页
        self.file_transfer_frame = tk.Frame(self.notebook)
        self.notebook.add(self.file_transfer_frame, text="文件传输")

        # 上传按钮
        self.upload_button = tk.Button(self.file_transfer_frame, text="上传文件", command=self.upload_file)
        self.upload_button.pack(pady=5)

        # 下载按钮
        self.download_button = tk.Button(self.file_transfer_frame, text="下载文件", command=self.download_file)
        self.download_button.pack(pady=5)
        
        # 创建远程文件编辑标签页
        self.remote_edit_frame = tk.Frame(self.notebook)
        self.notebook.add(self.remote_edit_frame, text="远程文件编辑")

        # 打开文件按钮
        self.open_remote_file_button = tk.Button(self.remote_edit_frame, text="打开远程文件", command=self.open_remote_file)
        self.open_remote_file_button.pack(pady=5)  
        
        # 保存文件按钮
        self.save_remote_file_button = tk.Button(self.remote_edit_frame, text="保存远程文件", command=self.save_remote_file)
        self.save_remote_file_button.pack(pady=5)   
         
        # 远程文件编辑区域
        self.remote_edit_text = scrolledtext.ScrolledText(self.remote_edit_frame, height=10, width=50)
        self.remote_edit_text.pack(fill=tk.BOTH, expand=True)     
        
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
        
    def execute_script(self):
        script = self.script_text.get("1.0", tk.END).strip()
        self.executor.submit(self.execute_command_in_thread, script)

        if self.ssh_client:        
            self.executor.submit(self.execute_remote_command, script)
        else:
            self.executor.submit(self.execute_local_command, script)
            
    def upload_file(self):
        if not self.ssh_client:
            messagebox.showerror("错误", "请先连接 SSH 服务器")
            return        
        local_file_path = filedialog.askopenfilename()
        if not local_file_path:
            return

        remote_path = simpledialog.askstring("远程路径", "输入远程路径:")
        if not remote_path:
            return            
        self.executor.submit(self.upload_file_in_thread, local_file_path, remote_path)    
        
    def upload_file_in_thread(self, local_file_path, remote_path):
        try:
            sftp = self.ssh_client.open_sftp()
            sftp.put(local_file_path, remote_path)
            self.update_result_text(f"文件已上传至 {remote_path}")
        except Exception as e:
            self.update_result_text(f"文件上传失败: {e}")   
             
    def download_file(self):
        if not self.ssh_client:
            messagebox.showerror("错误", "请先连接 SSH 服务器")
            return

        remote_file_path = simpledialog.askstring("远程文件路径", "输入远程文件路径:")
        if not remote_file_path:
            return

        local_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not local_path:
            return

        self.executor.submit(self.download_file_in_thread, remote_file_path, local_path)

    def download_file_in_thread(self, remote_file_path, local_path):
        try:
            sftp = self.ssh_client.open_sftp()
            sftp.get(remote_file_path, local_path)
            self.update_result_text(f"文件已下载至 {local_path}")
        except Exception as e:
            self.update_result_text(f"文件下载失败: {e}")  
            
    def open_remote_file(self):
        if not self.ssh_client:
            messagebox.showerror("错误", "请先连接 SSH 服务器")
            return

        remote_file_path = simpledialog.askstring("远程文件路径", "输入远程文件路径:")
        if not remote_file_path:
            return

        self.executor.submit(self.open_remote_file_in_thread, remote_file_path)
        
    def open_remote_file_in_thread(self, remote_file_path):
        try:
            sftp = self.ssh_client.open_sftp()
            with sftp.open(remote_file_path, 'r') as f:
                file_content = f.read().decode()
                self.remote_edit_text.delete("1.0", tk.END)
                self.remote_edit_text.insert(tk.END, file_content)
        except Exception as e:
            self.update_result_text(f"打开远程文件失败: {e}")
            
    def save_remote_file(self):
        if not self.ssh_client:
            messagebox.showerror("错误", "请先连接 SSH 服务器")
            return

        remote_file_path = simpledialog.askstring("远程文件路径", "输入远程文件路径:")
        if not remote_file_path:
            return

        file_content = self.remote_edit_text.get("1.0", tk.END).strip()
        self.executor.submit(self.save_remote_file_in_thread, remote_file_path, file_content)
        
    def save_remote_file_in_thread(self, remote_file_path, file_content):
        try:
            sftp = self.ssh_client.open_sftp()
            with sftp.open(remote_file_path, 'w') as f:
                f.write(file_content.encode())
            self.update_result_text(f"远程文件已保存: {remote_file_path}")
        except Exception as e:
            self.update_result_text(f"保存远程文件失败: {e}")

    def say(self, message):
        print(message)
        self.update_result_text(message)
                     
    def show_history(self):
        history_str = "\n".join(self.history)
        simpledialog.messagebox.showinfo("命令历史记录", history_str)    
                                 
def execute_script(script_file):
    try:
        with open(script_file) as file:
            script = file.read()
            execute_command(script)
    except FileNotFoundError:
        print(f"Script file '{script_file}' not found.")
    except Exception as e:
        print(f"Error executing script: {e}")   

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
