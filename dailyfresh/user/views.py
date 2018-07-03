import re
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from user.models import *
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from dailyfresh import settings
from django.http import HttpResponse
from django.core.mail import send_mail
from user import tasks
from django.contrib.auth import authenticate, login,logout
from utils.mixin_util import LoginRequiredMixin


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

        # celery异步调用任务
        tasks.task_register_send_email.delay(user.id, username, email)

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
        '''显示登录页面'''
        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        # 使用模板
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        '''登录校验'''
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 业务处理:登录校验
        user = authenticate(username=username, password=password)

        print('user', user)

        if user != None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)

                # 获取登录后所要跳转到的地址
                # 如果找不到默认跳转到首页
                next_url = request.GET.get('next', default=reverse('goods:index'))

                # 跳转到next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')

                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')

                # 返回response
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})

class LogoutView(View):
    '''退出登录'''

    def get(self, request):
        '''退出登录'''
        # 清除用户的session信息
        request.session.flush()
        logout(request)

        # 跳转到首页
        return redirect(reverse('goods:index'))

# views.UserInfoView.as_view()
class UserInfoView(LoginRequiredMixin, View):
    '''用户中心-信息页'''

    def get(self, request):
        user = request.user
        try:
            address = Address.objects.get(user=user, is_default=True) # models.Manager
        except Address.DoesNotExist:
            # 不存在默认收货地址
            address = None

        context = {
            'page': '1',
            'address':address
        }
        return render(request, 'user_center_info.html', context)


class UserOrderView(LoginRequiredMixin, View):
    '''用户中心-信息页'''

    def get(self, request):
        context = {'page': '2'}
        return render(request, 'user_center_order.html', context)


class UserAddressView(LoginRequiredMixin, View):
    '''用户中心-信息页'''

    def get(self, request):
        '''显示'''
        # 获取登录用户对应User对象
        user = request.user

        # 获取用户的默认收货地址
        try:
            address = Address.objects.get(user=user, is_default=True) # models.Manager
        except Address.DoesNotExist:
            # 不存在默认收货地址
            address = None

        #数据字典
        context = {
            'page': '3',
            'address':address
        }

        #渲染
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        '''地址的添加'''
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        # 业务处理：地址添加
        # 用户新添加的地址作为默认收货地址，如果原来有默认地址，要取消
        # 获取用户的默认收货地址

        # 获取登录用户对应User对象
        user = request.user
        try:
            address = Address.objects.get(user=user, is_default=True)
            address.is_default=False
            address.save()
        except Address.DoesNotExist:
            # 不存在默认收货地址
            pass

        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=True)

        # 返回应答,刷新地址页面
        return redirect(reverse('user:address'))  # get请求方式


