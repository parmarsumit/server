#-*- coding: utf-8 -*-

import os
import sys
import logging

from ilot.core.manager import AppManager

# set database settings
if os.environ.get('DJANGO_ENV', 'dev') == 'production':
    DEBUG = False
else:
    DEBUG = True

LIB_ROOT = os.path.dirname(os.path.dirname(__file__))

SERVER_ROOT = os.environ.get('ILOT_SRV_ROOT', '/srv')
APP_ROOT = os.environ.get('ILOT_APP_ROOT', LIB_ROOT)

SECRET_KEY = "fsldjkhgljkfshfgnlcuqsngfiu"

APPEND_SLASH = False

USE_TZ = True
TIME_ZONE = 'Etc/UTC'

LANGUAGE_CODE = 'fr'
LANGUAGES = ('fr', 'en', )

LOCALE_PATHS = (
    os.path.join(APP_ROOT, 'locale'),
)

# User authentication urls configuration.
LOGIN_URL = '/admin/login/'
LOGOUT_URL = '/admin/logout/'
LOGIN_REDIRECT_URL = '/'

ALLOWED_HOSTS = ["*"]

STATIC_ROOT = SERVER_ROOT+"/static/"
STATIC_URL = "/static/"

MEDIA_ROOT = SERVER_ROOT+'/media/'
MEDIA_URL = '/media/'

BUILD_ROOT = APP_ROOT+"/build/"
THEME_ROOT = APP_ROOT+"/theme/"

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

STATICFILES_DIRS = (THEME_ROOT, BUILD_ROOT)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "ilot",
    "ilot.api",
    "ilot.core",
    "ilot.data",
    "ilot.meta",
    "ilot.medias",
    "ilot.rules",
    "ilot.grammar",
    #"ilot.scenarios",
    "ilot.webhooks",
    "ilot.cloud",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_swagger",
    "django_filters",
    "django_mailjet",
    "mathfilters"
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
#        'django_filters.SearchFilter', 'django_filters.OrderingFilter',
    ),
     'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
        'user': '1000/day'
    }
}

MIDDLEWARE_CLASSES = (
    #'ilot.cloud.middleware.GithubDeployMiddleware',
#    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    #"ilot.core.middleware.multilingual.MultilingualURLMiddleware",
    'ilot.multibase.RouterMiddleware',
    "ilot.core.middleware.profiler.CProfileMiddleware",
)

DATETIME_FORMATS = (('c'),)
DATETIME_FORMAT = DATETIME_FORMATS[0]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


#
CACHE_CORE_QUERIES = True
CACHE_TYPED_LISTS = True

#
SHOW_DEBUG_SQL = False

# debug database stands in the user folder .ilot
from os.path import expanduser
HOME_ROOT = expanduser("~")

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'ilot',
            'USER': 'ilot',
        }
    }
else:
    DATABASES = {
        'default':{
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': SERVER_ROOT+'/.ilot.db',
         }
    }

if DEBUG:
    T_LOADERS = [
        ('django.template.loaders.locmem.Loader', AppManager.get_core()),
        'ilot.templates.Loader',
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]
else:
    T_LOADERS = [
        ('django.template.loaders.locmem.Loader', AppManager.get_core()),
         ('django.template.loaders.cached.Loader', [
            'ilot.templates.Loader',
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (APP_ROOT+"/templates/",),
        #'APP_DIRS': True,
        'OPTIONS': {
            'loaders': T_LOADERS,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #'django.core.context_processors.request',
            ],
        },
    },
]

URLS_WITHOUT_LANGUAGE_REDIRECT = ('/sitemap.xml',
                                  '/robots.xml',
                                  '/humans.txt',
                                  '/favicon.ico',
                                  '/admin')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 100, #60 * 60 * 24,  # 24 hours
    },
}

MARKDOWN_DEUX_HELP_URL = '/'
MARKDOWN_DEUX_DEFAULT_STYLE = {
    "extras": {
        "code-friendly": None,
    },
    "safe_mode": "escape",
}
MARKDOWN_DEUX_STYLES = {"default": MARKDOWN_DEUX_DEFAULT_STYLE}

#
logging.captureWarnings(True)

catch_all_handlers = ["console"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S"
        },
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s [%(name)s:%(lineno)s] %(process)d %(thread)d %(message)s"
        },
        "console": {
            "format": "[%(asctime)s] %(levelname)5s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%H:%M:%S"
        }
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": False,
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console",
            "stream": sys.stdout
        },
    },
    "loggers": {
        "": {
            "handlers": catch_all_handlers,
            "level": "DEBUG",
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.startup": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR"
        },
        "django.db.backends": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.commands": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "app": {
            "handlers": ["console"],
            "level": "INFO"
        }
    }
}
if SHOW_DEBUG_SQL:
    LOGGING['loggers']["django.db.backends"]['level'] = 'DEBUG'

import os

CLOUD = False

# set database settings
if os.environ.get('DJANGO_ENV', 'dev') == 'production':
    DEBUG = False
    TEMPLATE_DEBUG = False

WSGI_APPLICATION = "ilot.wsgi.application"

#SESSION_COOKIE_DOMAIN = AppManager.get_project_cname()
#SESSION_COOKIE_NAME = AppManager.get_project_id()
#SESSION_COOKIE_SECURE = True
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

#DATABASE_ROUTERS = ['ilot.multibase.DatabaseRouter']

ROOT_URLCONF = "ilot.urls"

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'in-v3.mailjet.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'ebeeb0718e7a52640b5a20bae28a28f7')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '1801ea9757a5445761b02aede88a90aa')
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'contact@ilot.online'

SERVER_EMAIL = 'contact@ilot.online'
CONTACT_EMAIL = 'contact@ilot.online'

EMAIL_BACKEND = 'django_mailjet.backends.MailjetBackend'

MAILJET_API_KEY = 'ebeeb0718e7a52640b5a20bae28a28f7'
MAILJET_API_SECRET = '1801ea9757a5445761b02aede88a90aa'

ADMINS = ['nicolas@biodigitals.com']

#
SECRET_KEY = 'ffdqsg)z8@q0qfsdreI89è§FDS1oxudm08mz=w°04./S8f&)'
