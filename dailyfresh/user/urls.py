from django.conf.urls import url
from user import views

urlpatterns = [
    url(r'^register$', views.RegisterView.as_view(), name='register'),# 注册
]