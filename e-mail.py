import smtplib
from email.mime.text import MIMEText

def send_email(subject, message, sender, receiver):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
                    
    smtp_server = smtplib.SMTP('smtp.example.com', 587)
    smtp_server.starttls()
    smtp_server.login('username', 'password')
    smtp_server.sendmail(sender, [receiver], msg.as_string())
    smtp_server.quit()

# 要发送的邮件内容
email_subject = input("主题：")
email_message = input("内容：")
recipient_email = input("邮箱地址：")
print = (email_subject)
print = (email_message)
print = (recipient_email)

# 调用发送邮件函数
send_email(email_subject, email_message, 'sender@example.com', recipient_email)