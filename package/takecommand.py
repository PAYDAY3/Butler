import azure.cognitiveservices.speech as speechsdk
from my_package import Logging

logging = Logging.getLogger(__name__)

def takecommand():
    # 替换为你的 Azure 订阅密钥和服务区域
        speech_key = "your_subscription_key"
        service_region = "chinaeast2"
        
        # 配置 Azure 语音服务
        speech_config.speech_synthesis_language = "zh-CN"
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

        print("请说话...")

        try:
            # 开始语音识别
            result = recognizer.recognize_once()

            # 处理识别结果
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                query = result.text
                print('User: ' + query + '\n')
                return query
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("对不起，我没有听清楚，请再说一遍。")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"语音识别取消: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"错误详情: {cancellation_details.error_details}")
                return None

        except Exception as e:
            print(f"语音识别出错: {e}")
            logging.error(f"语音识别出错: {e}")
            return None