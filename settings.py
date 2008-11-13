from localsettings import MUSIC_HUB_FOLDER, ADMINS, SECRET_KEY

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('MusicHub Admin', 'alex@grep.ro'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = MUSIC_HUB_FOLDER + 'db.sqlite'

TIME_ZONE = 'Europe/Bucharest'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False

MEDIA_ROOT = MUSIC_HUB_FOLDER + 'files/'
MEDIA_URL = '/files/'

ADMIN_MEDIA_PREFIX = '/admin-media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'music_hub.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'music_hub',
)
