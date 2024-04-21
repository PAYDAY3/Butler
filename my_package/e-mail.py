# -*- coding: utf-8 -*-
import imaplib
import email
import time
import datetime
from Logging import getLogger, readLog
from dateutil import parser
import smtplib
from email.mime.text import MIMEText
from email.header import Header

your_password = ""#邮箱密码
Email_address = "@qq.com"#邮箱地址
class Plugin():

    SLUG = "email"

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
        """Whether the email is sent by the user"""
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
        if sub.strip() == "":
            return ""
        to_read = config.get("/email/read_email_title", True)
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
        
    def send_email(self, subject, message, receiver):
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = Email_address  # 发件人地址
        msg['To'] = receiver
        
        # 设置 SMTP 服务器地址和端口
        smtp_server = 'smtp.qq.com'  # 修改为你的SMTP服务器地址
        smtp_port = 587  # 一般情况下使用587端口
        
        # 登录 SMTP 服务器并发送邮件
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # 开启安全传输模式（TLS）
            server.login(Email_address, your_password)  # 修改为你的邮箱密码
            server.sendmail(Email_address, [recipient_email], msg.as_string())
            print("邮件发送成功！")
        except Exception as e:
            print("邮件发送失败:", e)
        finally:
            server.quit()

# 实例化插件对象
email_plugin = Plugin()

# 要发送的邮件内容
email_subject = input("主题：")
email_message = input("内容：")
recipient_email = input("邮箱地址：")
print(email_subject)
print(email_message)
print(recipient_email)

# 调用发送邮件函数
send_email(email_subject, email_message, Email_address, recipient_email)
