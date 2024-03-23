from pocketsphinx import LiveSpeech
import subprocess
import speech_recognition as sr

def setup_recognizer():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1  # 静态能量阈值
    recognizer.dynamic_energy_adjustment_damping = 0.15  # 调整阈值的平滑因子
    recognizer.dynamic_energy_ratio = 1.5  # 阈值调整比率
    recognizer.operation_timeout = 5  # 最长等待时间（秒）
    recognizer.energy_threshold = 4000  # 设置音量阈值
    recognizer.dynamic_energy_threshold = True  # 自动调整音量阈值
    return recognizer

def takecommand():
    recognizer = setup_recognizer()

    # 设置自定义语音识别模型文件的路径
    language_model_path = "cmusphinx-zh-cn/zh_cn.lm.bin"
    dictionary_path = "cmusphinx-zh-cn/zh_cn.dict"
    
    # 设置模型文件路径
    recognizer.default = 'my_snowboy/jarvis.umdl'

    with sr.Microphone() as source:
        print("请说话...")
        audio = recognizer.listen(source, phrase_time_limit=5)

    try:
        text = recognizer.recognize_sphinx(audio, language='zh-CN', language_model_path, dictionary_path)  # 使用Sphinx引擎进行本地识别
        print("识别结果: " + text)
        # 在这里添加根据识别结果执行其他操作的逻辑
    except sr.UnknownValueError:
        print("无法识别，请重试")
    except sr.RequestError as e:
        print("请求出错：{0}".format(e))