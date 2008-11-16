from urllib import quote

def _now():
    from datetime import datetime
    import time
    t = time.time()
    timezone = (datetime.fromtimestamp(t) - datetime.utcfromtimestamp(t)).seconds
    zonestr = "%+03d:%02d" % (timezone/3600, timezone%3600/60)
    return datetime.fromtimestamp(t).strftime('%Y-%m-%dT%H:%M:%S') + zonestr

def log_event(kind, user, ip, txt):
    from django.conf import settings
    message = "%s [%s] user: %s; %s\n" % (_now(), kind, user, txt)
    f = open(settings.MUSIC_HUB_FOLDER + "events.log", 'a')
    f.write(message)
    f.close()

def _log_song_event(kind, request, song):
    log_event(kind=kind,
        user="%s (%d)" % (quote(request.user.username), request.user.id),
        ip=request.META['REMOTE_ADDR'],
        txt="original_filename: %s; code: %s; file_size: %d" % (
            quote(song.original_name), quote(song.get_code()), song.data_file.size)
    )

def log_song_upload(request, song):
    _log_song_event('upload', request, song)

def log_song_download(request, song):
    _log_song_event('download', request, song)

def log_song_delete(request, song):
    _log_song_event('delete', request, song)
