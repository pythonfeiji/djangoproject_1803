from django.conf.urls import url
from cart import views

urlpatterns = [
    url(r'^add$', views.CartAddView.as_view(), name='add'), # 购物车记录添加
]
