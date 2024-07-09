import subprocess
import speech_recognition as sr
import tempfile
import Logging
from speak import speak

model = "my_Snowboy/jarvis.umdl"  # Snowboy 模型文件路径

logging = logging.getLogger(__name__)

def takecommand():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("请说话...")
        recognizer.pause_threshold = 1  
        recognizer.dynamic_energy_adjustment_damping = 0.15
        recognizer.dynamic_energy_ratio = 1.5
        recognizer.operation_timeout = 5 
        recognizer.energy_threshold = 4000      
        recognizer.dynamic_energy_threshold = True  
        recognizer.default = model
        audio = recognizer.listen(source, phrase_time_limit=5)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            audio_file_path = f.name
            f.write(audio.get_wav_data())
            
            # 使用 Snowboy 进行唤醒词检测
            try:
                from my_snowboy.snowboydecoder import HotwordDetector
                detector = HotwordDetector(model)
                result = detector.detect(audio_file_path)
                if result:
                    logging.info("唤醒词检测成功")
                    
                    # 识别语音
                    try:
                        print("Recognizing...")  # 识别中...
                        query = recognizer.recognize_sphinx(audio, language='zh-CN')
                        print('User: ' + query + '\n')
                        return query  
                    except sr.UnknownValueError:
                        print("对不起，我没有听清楚，请再说一遍。")
                        speak("对不起，我没有听清楚，请再说一遍。")
                        return None
                    except sr.RequestError as error:
                        print(f"语音识别请求出错：{error}")
                        logging.error(f"语音识别请求出错：{error}")
                        return ""
                    except Exception as e:
                        print(f"语音识别出错: {e}")
                        logging.error(f"语音识别出错: {e}")
                        return None
                else:
                    print("没有检测到唤醒词")
                    logging.info("没有检测到唤醒词")
                    return None
            except Exception as e:
                print(f"Snowboy 检测出错: {e}")
                logging.error(f"Snowboy 检测出错: {e}")
                return None 
