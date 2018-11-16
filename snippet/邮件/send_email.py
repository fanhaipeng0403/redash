import smtplib
from email.mime.text import MIMEText


def send_email(from_addr="938376959@qq.com", email_password="rpsqlbpfsplxbeie", **kwargs):
    #### QQ的SMTP配置, 设置----> 账户----> 授权码
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    to_addrs = kwargs['to_addrs']
    subject = kwargs['subject']

    #### 邮件内容
    msg = MIMEText(kwargs['content'], 'plain', 'utf-8')
    msg['From'] = from_addr
    msg['Subject'] = kwargs['subject']

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.set_debuglevel(True)
        server.login(from_addr, email_password)
        server.sendmail(from_addr, to_addrs, msg.as_string())
    except Exception as e:
        print(e)
    else:
        print("Email sent: %s" % subject)
    finally:
        server.quit()


if __name__ == '__main__':
    send_email(to_addrs="515409351@qq.com", content='测试邮件啊', subject='这是一封测试邮件')
