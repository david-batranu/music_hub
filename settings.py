# Django settings for music_hub project.

MUSIC_HUB_FOLDER = '/tmp/'

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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = MUSIC_HUB_FOLDER + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/admin-media/'

SECRET_KEY = '+%(&+3&guiut5=f4$v3b)d@jcu&2wy@(*p((3f#@ya%75sx^-0'

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
    'music_hub',
)
