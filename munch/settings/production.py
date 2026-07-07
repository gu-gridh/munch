from .base import *
import os

DEBUG = True

#MEDIA_ROOT = os.getenv("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))
#MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
#STATIC_ROOT = os.getenv("STATIC_ROOT", os.path.join(BASE_DIR, "static_build"))
#STATIC_URL = os.getenv("STATIC_URL", "/static/")

MEDIA_ROOT = '/data/cdhdata/public/munch/static/'
MEDIA_URL  = 'https://data.dh.gu.se/munch/static/'
ORIGINAL_URL    = 'https://data.dh.gu.se/munch/static/'
IIIF_URL        = 'https://img.dh.gu.se/munch/static/'

# ManifestStaticFilesStorage is recommended in production, to prevent
# outdated JavaScript / CSS assets being served from cache.
# See https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

FILE_UPLOAD_TIMEOUT = 60000  # 600 seconds (10 minutes)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5125450000
FILE_UPLOAD_MAX_MEMORY_SIZE = 5125450000


ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'your-domain.com,www.your-domain.com').split(',')
CSRF_TRUSTED_ORIGINS = ["https://munch.dh.gu.se", "http://localhost:8901"]

# Additional production settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('HOST'),
        'PORT': os.getenv('PORT'),
    }
    }
