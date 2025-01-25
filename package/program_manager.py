import os
import platform
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from jarvis import takecommand
import winreg
from datetime import datetime
import locale

Jarvis = takecommand()

class ProgramManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Program Manager 1.0")
        self.root.geometry("800x600")
        
        # 设置中文显示
        locale.setlocale(locale.LC_ALL, 'zh_CN')
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        self.tree = ttk.Treeview(self.main_frame, 
                                columns=("name", "size", "install_date"),
                                show="headings")
        
        # 定义列
        self.tree.heading("name", text="程序名称")
        self.tree.heading("size", text="大小")
        self.tree.heading("install_date", text="安装时间")
        
        # 设置列宽
        self.tree.column("name", width=300)
        self.tree.column("size", width=100)
        self.tree.column("install_date", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", 
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 状态栏
        self.status_bar = tk.Label(self.root, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 加载程序数据
        self.load_programs()
        
        # 添加控制按钮
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        self.delete_button = ttk.Button(self.control_frame, text="删除文件夹中的所有文件", command=self.on_delete_files)
        self.delete_button.pack(side=tk.LEFT, padx=10)
        
        self.uninstall_button = ttk.Button(self.control_frame, text="卸载选定的软件", command=self.on_uninstall)
        self.uninstall_button.pack(side=tk.LEFT, padx=10)
        
    def get_program_size(self, path):
        """获取程序占用空间"""
        try:
            if os.path.exists(path):
                size = os.path.getsize(path)
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024:
                        return f"{size:.2f} {unit}"
                    size /= 1024
            return "未知"
        except:
            return "未知"
    
    def get_install_date(self, key_path):
        """获取程序安装日期"""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                                winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            install_date = winreg.QueryValueEx(key, "InstallDate")[0]
            winreg.CloseKey(key)
            date = datetime.strptime(str(install_date), "%Y%m%d")
            return date.strftime("%Y年%m月%d日")
        except:
            return "未知"
    
    def load_programs(self):
        """加载已安装程序信息"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_size = 0
        program_count = 0
        
        keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for key_path in keys:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                
                subkey_count = winreg.QueryInfoKey(key)[0]
                
                for i in range(subkey_count):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey_path = f"{key_path}\\{subkey_name}"
                        subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                              subkey_path, 0, 
                                              winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                        
                        try:
                            program_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            
                            size = self.get_program_size(install_location)
                            if size != "未知":
                                total_size += float(size.split()[0])
                            
                            install_date = self.get_install_date(subkey_path)
                            
                            self.tree.insert("", tk.END, values=(program_name, size, install_date))
                            program_count += 1
                            
                        except:
                            continue
                            
                        winreg.CloseKey(subkey)
                        
                    except:
                        continue
                        
                winreg.CloseKey(key)
                
            except:
                continue
        
        self.status_bar.config(
            text=f"共计 {program_count} 个程序占用空间 {total_size:.2f} GB")
        
        self.root.after(30000, self.load_programs)

    def on_delete_files(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            jarvis_command = f"delete_all_files_in_folder {folder_path}"
            Jarvis.execute(jarvis_command)
            messagebox.showinfo("成功", f"{folder_path} 中的所有文件已删除。")

    def on_uninstall(self):
        selected_item = self.tree.selection()
        if selected_item:
            program_name = self.tree.item(selected_item, "values")[0]
            uninstall_program(program_name)
            clean_residual_files(program_name)
            messagebox.showinfo("成功", f"{program_name} 已被卸载并清理。")

def main():
    root = tk.Tk()
    app = ProgramManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
