"""
Django settings for saltshaker project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import django_crontab.crontab
# celery
import djcelery
from celery import Celery, platforms
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't@r05nl_m2jp8*=(rkn)r+$7n(jujyt@uviwy(4$$@+t&@yry8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#SESSION_COOKIE_AGE = 60*60

ALLOWED_HOSTS = []

# django-crontab
CRONJOBS = (
    #('*/1 * * * *', 'shaker.cron.dashboard_scheduled_job'),
    #('*/1 * * * *', 'shaker.cron.minions_status_scheduled_job'),
    #('*/1 * * * *', 'shaker.cron.grains_scheduled_job'),
    ('*/1 * * * *', 'shaker.cron.dashboard_queue_scheduled_job'),
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'shaker',
    'jenkins_wrapper',
    'account',
    'code_update',
    'dashboard',
    'execute',
    'groups',
    'jobs',
    'minions',
    'states_config',
    'files_manager',
    'utility',
    'system_setup',
    'returner',
    'djcelery',
    'middleware',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    #customized middleware
    'middleware.django_slow_log.SlowLogMiddleware',
    'middleware.access_log.CustomerLogMiddleware',
)

ROOT_URLCONF = 'saltshaker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'saltshaker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'saltshake', # Or path to database file if using sqlite3.
        'USER': 'saltshake', # Not used with sqlite3.
        'PASSWORD': 'saltshake', # Not used with sqlite3.
        'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306', # Set to empty string for default. Not used with sqlite3.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)


# SaltStack API
SALT_API_URL = 'http://127.0.0.1:8000'
SALT_API_USER = 'admin'
SALT_API_PASSWD = 'admin'

# File root directory
FILE_BASE_DIR = '/srv/salt/'

# django logging
CUSTOM_ACCESS_LOG_OPEN = True
DJANGO_SLOW_LOG_OPEN = True
DJANGO_SLOW_LOG_TIME_DELTA = 3000  # int ms

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(module)s %(process)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'error': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'debug_verbose': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'django_slow': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        
        },
    },
    'handlers': {
        'shaker_default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/saltshaker/all.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'access': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/saltshaker/access.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/saltshaker/error.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'error',
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/saltshaker/debug.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'debug_verbose',
        },
        'django_slow': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/saltshaker/django_slow.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'django_slow',
        },

    },
    'loggers': {
        'django': {
            'handlers': ['shaker_default'],
            'level': 'INFO',
            'propagate': False
        },
        'access': {
            'handlers': ['access'],
            'level': 'INFO',
            'propagate': True
        },
        'error': {
            'handlers': ['error'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django_slow': {
            'handlers': ['django_slow'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
# celery + rabbitmq
platforms.C_FORCE_ROOT = True   # Running a worker with superuser privileges
djcelery.setup_loader()
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"