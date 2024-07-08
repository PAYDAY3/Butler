import speech_recognition as sr
import subprocess
import pexpect
import time
import os
import ptyprocess

# 预定义命令
commands = {
    "扫描端口": "nmap",
    "关闭Hydra": "pkill hydra",
    "ping": "ping",
    "whois": "whois"
}

# 日志记录函数
def log_command(command, result):
    with open("command_log.txt", "a", encoding='utf-8') as log_file:
        log_file.write(f"{datetime.datetime.now()}: {command}\n{result}\n\n")

# 语音识别函数
def recognize_speech():
    with sr.Microphone() as source:
        print("请开始说话")
        audio = sr.Recognizer().listen(source)
    try:
        audio_command = sr.Recognizer().recognize_google(audio, language='zh-CN')
        print(f"你说的是：{audio_command}")
        return audio_command
    except sr.UnknownValueError:
        print("听不懂你在说什么")
    except sr.RequestError as e:
        print(f"无法连接到语音识别服务：{e}")
    return None

def execute_command(command):
    """执行命令并记录结果"""
    result = ""
    try:
        # 检查是否为工具启动命令
        for tool_name, tool_command in tools.items():
            if tool_name in command:
                # 执行工具启动命令
                subprocess.run(f"{tool_command} &", shell=True)
                print(f"启动了 {tool_name} 工具...")
                # 在新的终端窗口中继续执行命令
                time.sleep(1)  # 等待工具启动完成
                os.system(f"gnome-terminal -x bash -c '{tool_command}'")
                return

        # 执行普通命令
        terminal_process.write(command.encode() + b'\n')
        terminal_process.write(b'\r')
        terminal_process.flush()
        
        if command == 'exit':
            return False
        elif command.startswith("扫描端口"):
            target = input("请输入目标IP地址或主机名：")
            if not target:
                print("请输入目标IP地址或主机名")
                return True
            cmd = f"nmap -p- -T4 {target}"
            print(f"即将执行的命令是：{cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(result.stdout)
            log_command(cmd, result.stdout)
        elif command.startswith("关闭Hydra"):
            result = subprocess.run("pkill hydra", shell=True, capture_output=True, text=True)
            print(result.stdout)
            log_command("pkill hydra", result.stdout)            
        elif command.startswith("ping"):
            target = input("请输入目标IP地址或主机名：")
            if not target:
                print("请输入目标IP地址或主机名")
                return True
            cmd = f"ping {target}"
            print(f"即将执行的命令是：{cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(result.stdout)
            log_command(cmd, result.stdout)
        elif command.startswith("whois"):
            domain = input("请输入域名：")
            if not domain:
                print("请输入域名")
                return True
            cmd = f"whois {domain}"
            print(f"即将执行的命令是：{cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(result.stdout)
            log_command(cmd, result.stdout)
        else:
            # 检查预设命令
            for key, value in commands.items():
                if key in command:
                    print(f"即将执行的命令是：{value}")
                    subprocess.run(value, shell=True)
                    break
            else:
                # 发送命令到模拟终端
                terminal_process.write(command.encode() + b'\n')
                terminal_process.write(b'\r')
                terminal_process.flush()
                if command == 'exit':
                    return False
                print(f"未知命令：{command}")
                try:
                    terminal_output = terminal_process.read_nonblocking(size=1024, timeout=1).decode()
                    print(terminal_output, end='')
                    log_command(command, terminal_output)
                except pexpect.exceptions.TIMEOUT:
                    pass
                except Exception as e:
                    print(f"Error: {e}")
                    log_command(command, f"Error: {e}")
                                    
    except Exception as e:
        print(f"Error: {e}")
        return True
    return True

def main():
    print("欢迎使用命令终端界面！")
    print("请输入命令，输入'exit'退出。")
    # 打开模拟终端
    master_fd, slave_fd = ptyprocess.openpty()
    terminal_process = ptyprocess.PtyProcess.spawn("bash", stdin=slave_fd, stdout=slave_fd, stderr=slave_fd)
    # 打开 terminal.py 程序
    child = pexpect.spawn("python terminal.py")
    child.expect("# ")  # 等待 terminal.py 显示提示符
    time.sleep(1)  # 等待 terminal.py 启动完成    
    # 读取终端输出    
    while True:
        try:
            data = terminal_process.read(size=1024, timeout=1).decode()
            if data:
                print(data, end='')
        except Exception as e:
            print(f"Error: {e}")
            break        
        command = recognize_speech()
        if not execute_command(command):
            break
        # 将命令发送到 terminal.py
        child.sendline(command)
        child.expect("# ")
        print(child.before)            
        execute_command(command, terminal_process)
        
    # 关闭终端进程
    terminal_process.close()
if __name__ == '__main__':
    main()
