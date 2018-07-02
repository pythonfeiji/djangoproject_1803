import re
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from user.models import *
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired,BadSignature
from dailyfresh import settings
from django.http import HttpResponse
from django.core.mail import send_mail

class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''进行注册处理'''
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        '''
        发送激活邮件，包含激活链接: http://ip:port/user/active/3
        激活链接中需要包含用户的身份信息, 并且要把身份信息进行加密
        '''
        # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode()

        # 发邮件
        subject = '天天生鲜欢迎信息'#主题
        message = ''#文本内容
        sender = settings.EMAIL_FROM#发件人
        receiver = [email]#收件人
        html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://192.168.12.42:8888/user/active/%s">http://192.168.12.42:8888/user/active/%s</a>' % (
        username, token, token)#html内容

        send_mail(subject, message, sender, receiver, html_message=html_message)


        # 返回应答, 跳转到首页
        return redirect(reverse('goods:index'))
        # return redirect('/index')



class ActiveView(View):
    '''用户激活'''

    def get(self, request, token):
        '''进行用户激活'''
        # 进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')
        except BadSignature as e:
            # 激活链接被修改
            return HttpResponse('激活链接非法')


class LoginView(View):
    '''登录'''

    def get(self, request):
        # 使用模板
        return render(request, 'login.html')
