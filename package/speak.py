import pyttsx3
from pydub import AudioSegment
from playsound import playsound
import os

# 定义音频文件路径
JARVIS_AUDIO_FILE = "./my_snowboy/resources/jarvis.wav"
OUTPUT_FILE = "./temp.wav"
FINAL_OUTPUT_FILE = "./final_output.wav"

# 创建语音合成引擎
engine = pyttsx3.init()

def speak(audio):
    # 合成语音
    engine.say(audio)
    engine.runAndWait()  # 播放合成语音

    # 加载音效文件
    jarvis_sound = AudioSegment.from_wav(JARVIS_AUDIO_FILE)

    # 加载合成语音文件
    synthetic_speech = AudioSegment.from_wav(OUTPUT_FILE)

    # 调整音量
    synthetic_speech = synthetic_speech.apply_gain(10)  # 提高合成语音的音量
    jarvis_sound = jarvis_sound.apply_gain(-10)  # 降低音效的音量
    
    # 合并音频片段
    combined_sound = jarvis_sound.overlay(synthetic_speech)

    # 添加混响效果
    combined_sound = combined_sound.apply_reverb(reverb=AudioSegment.reverb(duration=1000))

    # 保存混合后的音频
    combined_sound.export(FINAL_OUTPUT_FILE, format="wav")

    # 播放混合后的音频
    playsound(FINAL_OUTPUT_FILE)

    # 删除临时文件
    os.remove(OUTPUT_FILE)
