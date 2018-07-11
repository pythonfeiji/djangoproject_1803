from django.conf.urls import url
from order import views

urlpatterns = [
    url(r'^place$', views.OrderPlaceView.as_view(), name='place'),  # 提交订单页面显示
    url(r'^commit$', views.OrderCommitView.as_view(), name='commit'),  # 订单创建
    url(r'^pay$', views.OrderPayView.as_view(), name='pay'), # 订单支付
]
