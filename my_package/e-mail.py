# -*- coding: utf-8 -*-
import os
import json
import imaplib
import email
import time
import datetime
import Logging 
from dateutil import parser
from email.header import Header
from email.mime.base import MIMEBase
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from my_package.takecommand import takecommand
from plugin.plugin_interface import AbstractPlugin, PluginResult

your_password = "your_password"  # 请替换为您的实际密码
Email_address = "example@qq.com"  # 请替换为您的实际邮箱地址

class Plugin(AbstractPlugin):

    SLUG = "email"
    
    def valid(self) -> bool:
        return True
        
    def __init__(self):
        self.load_config()
        self.current_account_index = 0  # 默认使用第一个账户
        self.update_account_info()  
        self._logger = None
          
    def load_config(self):
        with open("./email_config.json", "r") as f:
            self.config = json.load(f)
            
    def init(self, logger: logging.Logger):
        self._logger = logger
         
    def get_name(self):
        return "send_email"

    def get_chinese_name(self):
        return "发送电子邮件"

    def get_description(self):
        return "发送电子邮件的接口。"      
             
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "receiver_email": {
                    "type": "string",
                    "description": "收件人邮箱地址",
                },
                "subject": {
                    "type": "string",
                    "description": "邮件主题",
                },
                "message": {
                    "type": "string",
                    "description": "邮件内容",
                },
                "attachment_path": {
                    "type": "string",
                    "description": "邮件附件文件地址，如果你需要将生成的文件通过邮件发送出去，你应该使用本字段。",
                },
            },
            "required": ["receiver_email", "subject", "message"],
        }             
        
    def update_account_info(self):
        account = self.config["accounts"][self.current_account_index]
        self.email = account["email"]
        self.password = account["password"]
        self.imap_server = account["imap_server"]
        self.imap_port = account["imap_port"]
        self.smtp_server = account["smtp_server"]
        self.smtp_port = account["smtp_port"]
         
    def say(self, message):
        print(message)        
        
    def switch_account(self, index):
        if 0 <= index < len(self.config["accounts"]:
            self.current_account_index = index
            self.update_account_info()
            print(f"已切换到账户: {self.email}")
        else:
            print("无效的账户索引")
            
    def getSender(self, msg):
        fromstr = str(msg["From"])
        ls = fromstr.split(" ")
        if len(ls) == 2:
            fromname = email.header.decode_header(str(ls[0]).strip('"'))
            sender = fromname[0][0]
        elif len(ls) > 2:
            fromname = email.header.decode_header(
                str(fromstr[: fromstr.find("<")]).strip('"')
            )
            sender = fromname[0][0]
        else:
            sender = msg["From"]
        if isinstance(sender, bytes):
            try:
                return sender.decode("utf-8")
            except UnicodeDecodeError:
                return sender.decode("gbk")
        else:
            return sender

    def isSelfEmail(self, msg):
        """邮件是否由用户发送"""
        fromstr = str(msg["From"])
        addr = (fromstr[fromstr.find("<") + 1 : fromstr.find(">")]).strip('"')
        address = config.get()[self.SLUG]["address"].strip()
        return addr == address

    def getSubject(self, msg):
        subject = email.header.decode_header(msg["subject"])
        if isinstance(subject[0][0], bytes):
            try:
                sub = subject[0][0].decode("utf-8")
            except UnicodeDecodeError:
                sub = subject[0][0].decode("gbk")
        else:
            sub = subject[0][0]
        to_read = False
        return sub.strip()
        if to_read:
            return "邮件标题为 %s" % sub
        return ""

    def isNewEmail(msg):
        """邮件是否为新邮件"""
        date = str(msg["Date"])
        dtext = date.split(",")[1].split("+")[0].strip()
        dtime = time.strptime(dtext, "%d %b %Y %H:%M:%S")
        current = time.localtime()
        dt = datetime.datetime(*dtime[:6])
        cr = datetime.datetime(*current[:6])
        return (cr - dt).days == 0

    def getDate(self, email):
        return parser.parse(email.get("date"))

    def getMostRecentDate(self, emails):
        dates = [self.getDate(e) for e in emails]
        dates.sort(reverse=True)
        if dates:
            return dates[0]
        return None
        
    def save_attachments(msg, download_folder="attachments"):
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue    
            if part.get('Content-Disposition') is None:
                continue   
            filename = part.get_filename()
            if bool(filename):
                filepath = os.path.join(download_folder, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                print(f"附件已保存：{filepath}")                         

    def fetchUnreadEmails(self, since=None, markRead=False, limit=None):
        logger = logging.getLogger(__name__)
        profile = config.get()
        conn = imaplib.IMAP4(
            profile[self.SLUG]["imap_server"], profile[self.SLUG]["imap_port"]
        )
        conn.debug = 0

        msgs = []
        try:
            conn.login(profile[self.SLUG]["address"], profile[self.SLUG]["password"])
            conn.select(readonly=(not markRead))
            (retcode, messages) = conn.search(None, "(UNSEEN)")
        except Exception:
            logger.warning("抱歉，您的邮箱账户验证失败了，请检查下配置")
            return None

        if retcode == "OK" and messages != [b""]:
            numUnread = len(messages[0].split(b" "))
            if limit and numUnread > limit:
                return numUnread

            for num in messages[0].split(b" "):
                # parse email RFC822 format
                ret, data = conn.fetch(num, "(RFC822)")
                if data is None:
                    continue
                msg = email.message_from_string(data[0][1].decode("utf-8"))

                if not since or self.getDate(msg) > since:
                    msgs.append(msg)

        conn.close()
        conn.logout()

        return msgs

    def handle(self, text, parsed):
        msgs = self.fetchUnreadEmails(limit=5)

        if msgs is None:
            self.say("抱歉，您的邮箱账户验证失败了", cache=True)
            return

        if isinstance(msgs, int):
            response = "您有 %d 封未读邮件" % msgs
            self.say(response, cache=True)
            return

        senders = [str(self.getSender(e)) for e in msgs]

        if not senders:
            self.say("您没有未读邮件，真棒！", cache=True)
        elif len(senders) == 1:
            self.say(f"您有来自 {senders[0]} 的未读邮件。{self.getSubject(msgs[0])}")
        else:
            response = "您有 %d 封未读邮件" % len(senders)
            unique_senders = list(set(senders))
            if len(unique_senders) > 1:
                unique_senders[-1] = ", " + unique_senders[-1]
                response += "。这些邮件的发件人包括："
                response += " 和 ".join(senders)
            else:
                response += "，邮件都来自 " + unique_senders[0]
            self.say(response)

    def isValid(self, text, parsed):
        return any(word in text for word in ["邮箱", "邮件"])
        
    def send_email(self, takecommand, subject, message, receiver, args: dict) -> PluginResult:
        receiver_email = args.get("receiver_email")
        subject = args.get("subject")
        message = args.get("message")
        attachment_path = args.get("attachment_path")
        
        # 创建一个MIMEMultipart对象，添加邮件内容和头部信息
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = Email_address  # 发件人地址
        msg['To'] = receiver
        
        # 邮件正文
        msg.attach(MIMEText(message, "plain", "utf-8"))            
        # 设置 SMTP 服务器地址和端口
        smtp_server = 'smtp.qq.com'  # 修改为你的SMTP服务器地址
        smtp_port = 587  # 一般情况下使用587端口
        
        # 添加附件
        if attachment_path is not None and attachment_path != "":
            with open(attachment_path, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=attachment_path)
            part['Content-Disposition'] = f'attachment; filename="{attachment_path}"'
            msg.attach(part)        
            
        # 登录 SMTP 服务器并发送邮件
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # 开启安全传输模式（TLS）
            server.login(Email_address, your_password)  # 修改为你的邮箱密码
            server.sendmail(Email_address, [recipient_email], msg.as_string())
            server.ehlo()
            server.close()
            return PluginResult.new(result="邮件发送成功", need_call_brain=True)
        except Exception as e:
            self._logger.error("发送邮件失败，异常: {}".format(e))
            return PluginResult.new(result="邮件发送失败", need_call_brain=True)
        finally:
            server.quit()
            
    def edit_email_content(self, content):
        """编辑邮件内容"""
        # 使用 textwrap 格式化文本
        content = textwrap.fill(content, width=80)
        # 获取用户输入的编辑内容
        edited_content = input(f"编辑邮件内容:\n{content}\n>>> ")
        return edited_content
        
def config_get():
    with open("./email_config.json", "r") as f:
        config = json.load(f)
    return config

# 实例化插件对象
email_plugin = Plugin()
email_plugin.switch_account(1)
# 要发送的邮件内容
email_subject = input("主题：")
email_message = input("内容：")
recipient_email = input("邮箱地址：")
print(email_subject)
print(email_message)
print(recipient_email)

# 编辑邮件内容
edited_message = email_plugin.edit_email_content(formatted_message)
print(edited_message)
# 调用发送邮件函数
send_email(email_subject, email_message, Email_address, recipient_email)
