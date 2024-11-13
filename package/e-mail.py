# -*- coding: utf-8 -*-
import os
import json
import imaplib
import email
import time
import datetime
from dateutil import parser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib

your_password = "your_password"  # 请替换为您的实际密码
Email_address = "example@qq.com"  # 请替换为您的实际邮箱地址

class Plugin():

    SLUG = "email"
    
    def __init__(self):
        self.load_config()
        self.current_account_index = 0
        self.update_account_info()  
          
    def load_config(self):
        with open("./email_config.json", "r") as f:
            self.config = json.load(f)
            
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
        if 0 <= index < len(self.config["accounts"]):
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
        address = self.config[self.SLUG]["address"].strip()
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
        return sub.strip()

    def isNewEmail(self, msg):
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
        
    def save_attachments(self, msg, download_folder="attachments"):
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
        profile = self.config
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
            print("抱歉，您的邮箱账户验证失败了，请检查下配置")
            return None

        if retcode == "OK" and messages != [b""]:
            for num in messages[0].split(b" "):
                ret, data = conn.fetch(num, "(RFC822)")
                if data is None:
                    continue
                msg = email.message_from_string(data[0][1].decode("utf-8"))
                if not since or self.getDate(msg) > since:
                    msgs.append(msg)

        conn.close()
        conn.logout()

        return msgs

    def send_email(self, subject, message, receiver):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = Email_address
        msg['To'] = receiver
        msg.attach(MIMEText(message, "plain", "utf-8"))            

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(Email_address, your_password)
            server.sendmail(Email_address, [receiver], msg.as_string())
            print("邮件发送成功！")
        except Exception as e:
            print("邮件发送失败:", e)
        finally:
            server.quit()
        
# 实例化插件对象
email_plugin = Plugin()
email_plugin.switch_account(1)

# 要发送的邮件内容
email_subject = input("主题：")
email_message = input("内容：")
recipient_email = input("邮箱地址：")

# 调用发送邮件函数
email_plugin.send_email(email_subject, email_message, recipient_email)
