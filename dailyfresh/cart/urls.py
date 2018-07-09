from django.conf.urls import url
from cart import views

urlpatterns = [
    url(r'^add$', views.CartAddView.as_view(), name='add'), # 购物车记录添加
    url(r'^count', views.CartCountView.as_view(), name='count'), # 购物车总数
    url(r'^$', views.CartInfoView.as_view(), name='show'), # 购物车页面显示
]
