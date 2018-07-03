from django.shortcuts import render
from django.views.generic import View


class IndexView(View):
    def get(self,request):
        '''
        1、根据session获取用户id   uid= request.session.get('_auth_user_id')
        2、根据uid获取user对象     user = User.objects.get(id=uid)
        3、渲染参数               return render(request, 'index.html', cxt = {'user':user})
        '''

        # 获取用户认证系统里的user
        # print('RegisterView-get...%s' % request.user)
        # print('RegisterView-get...%s' % request.user.is_authenticated())

        '''首页'''
        # return render(request, 'index.html', context = {'user':request.user})
        return render(request, 'index.html')
