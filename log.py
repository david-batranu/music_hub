from urllib import quote
from datetime import datetime

from pytz import timezone
from django.conf import settings

def log_event(kind, user, ip, txt):
    now = datetime.now(timezone(settings.TIME_ZONE)).strftime('%Y-%m-%dT%H:%M:%S%z')
    now = "%s:%s" % (now[:-2], now[-2:])
    message = "%s [%s] user: %s; %s\n" % (now, kind, user, txt)
    f = open(settings.MUSIC_HUB_FOLDER + "events.log", 'a')
    f.write(message)
    f.close()

def _log_file_event(kind, request, music_file):
    log_event(kind=kind,
        user="%s (%d)" % (quote(request.user.username), request.user.id),
        ip=request.META['REMOTE_ADDR'],
        txt="original_filename: %s; hashed_filename: %s" % (
            quote(music_file.original_name), quote(str(music_file.file)))
    )

def log_file_upload(request, music_file):
    _log_file_event('upload', request, music_file)

def log_file_download(request, music_file):
    _log_file_event('download', request, music_file)

def log_file_delete(request, music_file):
    _log_file_event('delete', request, music_file)
