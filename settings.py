DEBUG = True

ADMINS = (
    ('MusicHub Admin', 'musichub@example.com'),
)
MANAGERS = ADMINS

LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
TIME_ZONE = 'Europe/Bucharest'

MEDIA_URL = '/media/model-files/'
ADMIN_MEDIA_PREFIX = '/media/admin/'

from localsettings import *

TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = MUSIC_HUB_FOLDER + 'db.sqlite'
MEDIA_ROOT = MUSIC_HUB_FOLDER + 'files/'

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'music_hub.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django_evolution',
    'music_hub',
)
