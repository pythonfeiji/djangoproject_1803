from django.conf.urls import url
from order import  views

urlpatterns = [
    url(r'^place$', views.OrderPlaceView.as_view(), name='place'), # 提交订单页面显示
]
