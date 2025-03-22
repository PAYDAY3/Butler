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
            self.display_subtitle("正在聆听（5秒超时）...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(takecommand)
                try:
                    command = future.result(timeout=5).lower()
                    if not self._validate_command(command):
                        self.display_subtitle("检测到危险字符")
                        return ""
                    return command
                except TimeoutError:
                    self.display_subtitle("输入超时")
                    return ""
        except Exception as e:
            logging.error(f"Error processing voice input: {e}")
            self.display_subtitle("语音输入处理时出错。")
            return ""
            
    def _validate_command(self, command: str) -> bool:
        """命令安全性校验"""
        forbidden = [';', '&', '|', '`', '$']
        return all(c not in command for c in forbidden)
        
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
