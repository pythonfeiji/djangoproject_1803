from celery import task
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
# from dailyfresh import settings
import time


# 发邮件
@task
def task_register_send_email(uid, username, email):
    time.sleep(10)
    '''
        发送激活邮件，包含激活链接: http://ip:port/user/active/3
        激活链接中需要包含用户的身份信息, 并且要把身份信息进行加密
    '''
    # 加密用户的身份信息，生成激活token
    serializer = Serializer(settings.SECRET_KEY, 3600)
    info = {'confirm': uid}
    token = serializer.dumps(info).decode()

    # 发邮件
    subject = '天天生鲜欢迎信息'  # 主题
    message = ''  # 文本内容
    sender = settings.EMAIL_FROM  # 发件人
    receiver = [email]  # 收件人
    html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://192.168.12.42:8888/user/active/%s">http://192.168.12.42:8888/user/active/%s</a>' % (
        username, token, token)  # html内容

    send_mail(subject, message, sender, receiver, html_message=html_message)#发送

    print('发送成功。。。')
