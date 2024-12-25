from my_package import Logging
from jarvis import takecommand

logging = Logging.getLogger(__name__)

class InputProcessor:
    def __init__(self):
        """
        Initializes the InputProcessor class.
        """
        pass

    def display_subtitle(self, message: str) -> None:
        """
        Displays a subtitle message.
        
        Args:
            message (str): The message to be displayed.
        """
        print(message)

    def process_voice_input(self) -> str:
        """
        Processes voice input by activating voice input mode and capturing the command.
        
        Returns:
            str: The captured voice command.
        """
        try:
            self.display_subtitle("语音输入模式已激活，请开始说话...")
            wake_command = takecommand().lower()  # 调用 takecommand 函数
            print(f"请输入命令: {wake_command}")
            self.display_subtitle(f"语音输入: {wake_command}")
            logging.info(f"Voice command: {wake_command}")
            return wake_command
        except Exception as e:
            logging.error(f"Error processing voice input: {e}")
            self.display_subtitle("语音输入处理时出错。")
            return ""

    def process_text_input(self) -> str:
        """
        Processes text input by activating text input mode and capturing the command.
        
        Returns:
            str: The captured text input.
        """
        try:
            self.display_subtitle("文字手写输入模式已激活。输入 2 返回语音输入模式。")
            user_input = input("请输入命令: ").lower()
            print(f"请输入命令: {user_input}")
            self.display_subtitle(f"文字手写输入: {user_input}")
            logging.info(f"Text input: {user_input}")
            return user_input
        except Exception as e:
            logging.error(f"Error processing text input: {e}")
            self.display_subtitle("文字手写输入处理时出错。")
            return ""
