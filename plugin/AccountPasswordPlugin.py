import json
from cryptography.fernet import Fernet
from datetime import datetime
from abc import ABCMeta, abstractmethod
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand
from my_package import Logging

logging = Logging.getLogger(__name__)

class AccountPasswordPlugin(AbstractPlugin):
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        self.data_file = 'account_data.json'
        self.data = {}

    def valid(self) -> bool:
        # 检查密钥和加密套件是否正确初始化
        return self.key is not None and self.cipher_suite is not None

    def init(self, logging):
        self.logging = logging
        self.logging.info("AccountPasswordPlugin 初始化完成")

    def get_name(self):
        return "AccountPasswordPlugin"

    def get_chinese_name(self):
        return "账号密码插件"

    def get_description(self):
        return "一个用于保存和加密账号密码信息的插件"

    def get_parameters(self):
        return {
            "action": "str, required, 'save' 或 'retrieve'",
            "account": "str, action 为 'save' 时必需",
            "password": "str, action 为 'save' 时必需",
            "retrieve_account": "str, action 为 'retrieve' 时必需"
        }

    def on_startup(self):
        self.logging.info("AccountPasswordPlugin 启动")
        # 如果有现有数据，则加载
        try:
            with open(self.data_file, 'r') as f:
                encrypted_data = json.load(f)
                for account, enc_password in encrypted_data.items():
                    self.data[account] = self.cipher_suite.decrypt(enc_password.encode()).decode()
        except FileNotFoundError:
            self.logging.warning("未找到现有数据文件，开始新的数据文件。")
        except Exception as e:
            self.logging.error(f"加载数据时出错: {e}")

    def on_shutdown(self):
        self.logging.info("AccountPasswordPlugin 关闭")
        # 保存数据到文件
        try:
            encrypted_data = {account: self.cipher_suite.encrypt(password.encode()).decode() for account, password in self.data.items()}
            with open(self.data_file, 'w') as f:
                json.dump(encrypted_data, f)
        except Exception as e:
            self.logging.error(f"保存数据时出错: {e}")

    def on_pause(self):
        self.logging.info("AccountPasswordPlugin 暂停")

    def on_resume(self):
        self.logging.info("AccountPasswordPlugin 恢复")

    def run(self, takecommand: str, args: dict) -> PluginResult:
        start_time = datetime.now()
        action = args.get('action')

        if action == 'save':
            account = args.get('account')
            password = args.get('password')
            if not account or not password:
                return PluginResult.new(result="缺少账号或密码", need_call_brain=False, success=False, error_message="参数无效")

            self.data[account] = password
            result_message = f"账号 {account} 保存成功"

        elif action == 'retrieve':
            retrieve_account = args.get('retrieve_account')
            if not retrieve_account:
                return PluginResult.new(result="缺少要检索的账号", need_call_brain=False, success=False, error_message="参数无效")

            password = self.data.get(retrieve_account)
            if password is None:
                return PluginResult.new(result=f"未找到账号 {retrieve_account}", need_call_brain=False, success=False, error_message="账号未找到")

            result_message = f"账号 {retrieve_account} 的密码: {password}"

        else:
            return PluginResult.new(result="无效的操作", need_call_brain=False, success=False, error_message="未知操作")

        execution_time = (datetime.now() - start_time).total_seconds()
        return PluginResult.new(result=result_message, need_call_brain=False, success=True, execution_time=execution_time)
