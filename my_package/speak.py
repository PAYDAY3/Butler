import pyttsx3
def speak(text):
    # 为语音合成创建一个引擎实例
    engine = pyttsx3.init()
    # 将需要语音合成的文本传递给引擎
    engine.say(text)
    # 播放语音
    engine.runAndWait()