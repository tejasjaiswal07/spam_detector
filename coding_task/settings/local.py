from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']


SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_HOST = None
USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False
CORS_ALLOW_ALL_ORIGINS = True  


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'coding_task_db',
        'USER': 'postgres',
        'PASSWORD': 'Abcd@1234',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

SPECTACULAR_SETTINGS = {
    **SPECTACULAR_SETTINGS,  # Keep base settings
    'SERVE_PUBLIC': True,  # Allow public access to schema in development
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVE_AUTHENTICATION': None,
}
