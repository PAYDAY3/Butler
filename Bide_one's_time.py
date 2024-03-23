import time
import subprocess
from my_snowboy.snowboydecoder import snowboydecoder
import speech_recognition as sr

# 定义 Snowboy 唤醒器相关配置参数
models = ["snowboy/jarvis.pmdl"]  # 模型文件路径列表
sensitivity = [0.5]  # 敏感度列表
audio_gain = 1  # 录音设备增益
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity, audio_gain=audio_gain)

def main_control_program():
    # 主控程序逻辑
    while True:
        user_input = get_user_input()
        if user_input == "退出":
            break
        else:
            handle_command(user_input)

def get_user_input():
    # 获取用户语音输入
    print("请说话...")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        user_input = r.recognize_sphinx(audio, language="zh-CN")
        print(f"识别结果：{user_input}")
    except sr.UnknownValueError:
        print("无法识别语音")
        user_input = ""
    return user_input

def handle_command(command):
    # 处理用户命令
    print(f"处理命令：{command}")

def snowboy_detected_callback():
    # Snowboy 唤醒回调函数
    print("唤醒程序已触发")
    handle_command("唤醒词")

def interrupt_callback():
    # Snowboy 中断检测回调函数
    return False

def standby_program():
    print("待机程序已启动")
    while True:
        # 执行待机任务
        print("执行待机任务...")
        # 启动程序
        subprocess.Popen(["python", "jarvis.py"])
        # 进入低功耗模式，等待唤醒词
        detector.terminate()  # 终止唤醒器
        time.sleep(0.1)  # 等待0.1秒
        detector.start(interrupt_check=interrupt_callback, detected_callback=snowboy_detected_callback, sleep_time=0.03)
        
        time.sleep(5)  # 等待5秒钟

if __name__ == "__main__":
    # 运行 Snowboy 唤醒器
    detector.start(detected_callback=snowboy_detected_callback,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)
    try:
        standby_program()
    except KeyboardInterrupt:
        print("待机程序已停止")
