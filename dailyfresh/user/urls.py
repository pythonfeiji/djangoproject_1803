from django.conf.urls import url
from user import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^register$', views.RegisterView.as_view(), name='register'),# 注册
    url(r'^active/(?P<token>.*)$', views.ActiveView.as_view(), name='active'),  # 用户激活
    url(r'^login$', views.LoginView.as_view(), name='login'),  # 登录

    # url(r'^$', views.UserInfoView.as_view(), name='user'), # 用户中心-信息页
    # url(r'^order$', views.UserOrderView.as_view(), name='order'), # 用户中心-订单页
    # url(r'^address$', views.UserAddressView.as_view(), name='address'), # 用户中心-地址页



    url(r'^$', login_required(views.UserInfoView.as_view()), name='user'), # 用户中心-信息页
    url(r'^order$', login_required(views.UserOrderView.as_view()), name='order'), # 用户中心-订单页
    url(r'^address$', login_required(views.UserAddressView.as_view()), name='address'), # 用户中心-地址页
]