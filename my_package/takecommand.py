import subprocess
import speech_recognition as sr
import tempfile
from Logging import *
from speak import speak

model = "my_Snowboy/jarvis.umdl"  # Snowboy 模型文件路径

def setup_recognizer():
    recognizer = sr.Recognizer()   # 初始化语音识别器和文本到语音引擎
    global recognizer
    with sr.Microphone() as source:
        print("请说话...")
        recognizer.pause_threshold = 1  # 静态能量阈值
        recognizer.dynamic_energy_adjustment_damping = 0.15 # 调整阈值的平滑因子
        recognizer.dynamic_energy_ratio = 1.5  # 阈值调整比率
        recognizer.operation_timeout = 5  # 最长等待时间（秒）
        recognizer.energy_threshold = 4000      # 设置音量阈值
        recognizer.dynamic_energy_threshold = True  # 自动调整音量阈值
        recognizer.default = model
        audio = recognizer.listen(source, phrase_time_limit=5)
        # 将录制的音频保存为临时文件
        with tempfile.NamedTemporaryFile(delete=False) as f:
            audio_file_path = f.name + ".wav"
            f.write(audio.get_wav_data())
    return audio_file_path 
        try:
            print("Recognizing...")  # 识别中...
            query = recognizer.recognize_sphinx(audio, language='zh-CN')
            print('User: ' + query + '\n')
            return query     
        except Exception as e:
            print("对不起，我没有听清楚，请再说一遍。")
            speak("对不起，我没有听清楚，请再说一遍。")
            query = None
            return query
        except sr.RequestError as error:
            print(f"语音识别请求出错：{error}")
            logging.error(f"语音识别请求出错：{error}")
            return ""
