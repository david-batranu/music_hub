from urllib import quote
from datetime import datetime

from pytz import timezone
from django.config import settings

def log_event(kind, user, txt):
    now = datetime.now(timezone(settings.TIME_ZONE)).strftime('%Y-%m-%dT%H:%M:%S%z')
    message = "%s [%s] {%s} %s\n" % (now, kind, user, txt)
    open()

def log_file_upload(user, music_file):
    log_event(kind='upload',
        user="%s (%d)" % (quote(user.username), user.id),
        txt="original_filename: %s; hashed_filename: %s" % (
            quote(music_file.file_name), quote(str(music_file.file)))
    )

def log_file_delete(user, music_file):
    log_event(kind='delete',
        user="%s (%d)" % (quote(user.username), user.id),
        txt="original_filename: %s; hashed_filename: %s" % (
            quote(music_file.file_name), quote(str(music_file.file)))
    )
