from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'music_hub.views.index'),
    (r'^upload$', 'music_hub.views.upload'),
    (r'^delete$', 'music_hub.views.delete'),
    (r'^people/(?P<username>[^/]+)$', 'music_hub.views.person_page'),
    (r'^song/(?P<song_code>[0-9a-f]+)$', 'music_hub.views.song_page'),
    (r'^song/(?P<song_code>[0-9a-f]+)/download$', 'music_hub.views.download_song'),
    
    (r'^auth$', 'music_hub.views.auth'),
    
    (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    import os
    import music_hub
    music_hub_media = os.path.dirname(music_hub.__file__) + '/media'
    
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MUSIC_HUB_MEDIA_PREFIX[1:],
            'django.views.static.serve', {'document_root': music_hub_media})
    )
