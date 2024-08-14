from my_package import Logging
from jarvis import takecommand

logging = Logging.getLogger(__name__)

class InputProcessor:
    def __init__(self):
        pass

    def display_subtitle(self, message):
        print(message)

    def process_voice_input(self):
        self.display_subtitle("语音输入模式已激活，请开始说话...")
        wake_command = takecommand().lower()  # 调用 takecommand 函数
        print(f"请输入命令: {wake_command}")
        self.display_subtitle(f"语音输入: {wake_command}")
        logging.info("Voice command: " + wake_command)
        return wake_command

    def process_text_input(self):
        self.display_subtitle("文字手写输入模式已激活。输入 2 返回语音输入模式。")
        user_input = input("请输入命令: ").lower()
        print(f"请输入命令: {user_input}")
        self.display_subtitle(f"文字手写输入: {user_input}")
        logging.info("Text input: " + user_input)
        return user_input
