import os

HOST_IP = '192.168.12.42'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '*5-v-)2@+c#&x#4$izh)y_11jyqvp=ct_5$#qtlm@74fbi&q%b'

# DEBUG = True
# ALLOWED_HOSTS = []

DEBUG = False
ALLOWED_HOSTS = ['*',]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user',
    'goods',
    'djcelery',
    'tinymce',
    'haystack',
    'cart',
    'order',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'

#数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': HOST_IP,
        'PORT': '3306',
    }
}

#语言和时区
LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True
USE_L10N = True
# USE_TZ = True


#静态文件
STATIC_URL = '/static/'
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'static')
]
STATIC_ROOT='/var/www/dailyfresh/static/'

# django用户认证系统使用的模型类
AUTH_USER_MODEL='user.User'

#django用户认证系统登录的url
LOGIN_URL = '/user/login'

#发送邮件
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.126.com'#SMTP服务器
EMAIL_PORT = 25#端口号
EMAIL_HOST_USER = 'python_wangzha@126.com'#发送邮件的邮箱
EMAIL_HOST_PASSWORD = 'python1803'#在邮箱中设置的客户端授权密码
EMAIL_FROM = '天天生鲜<python_wangzha@126.com>'#收件人看到的发件人


# django-celery异步任务
import djcelery
djcelery.setup_loader()
BROKER_URL = 'redis://%s:6379/8'%HOST_IP
CELERY_IMPORTS = [
    'user.tasks',
]

#将session缓存到redis中
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = HOST_IP
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 1
SESSION_REDIS_PASSWORD = ''
SESSION_REDIS_PREFIX = 'session'


#tinymce默认样式配置
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'width': 600,
    'height': 400,
}


#FastDFS设置-自定义存储的类
DEFAULT_FILE_STORAGE = 'utils.fdfs.storage_util.FDFSStorage'
#FastDFS设置-客户端配置文件
FDFS_CLIENT_CONF = 'utils/fdfs/client.conf'
#FastDFS设置-url
FDFS_URL = 'http://%s:9999/'%HOST_IP




# Django的缓存配置  pip install django-redis-cache
CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "redis://192.168.12.42:6379/9",
        'TIMEOUT': 3600,
    },
}

# 连接redis的对象
from redis import StrictRedis
REDIS_CONN = StrictRedis(HOST_IP)



#全文检索HAYSTACK
HAYSTACK_CONNECTIONS = {
    'default': {
        #使用whoosh引擎
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
        # 'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        #索引文件路径
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}
#当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


#支付宝的设置

