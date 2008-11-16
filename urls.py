from django.conf.urls.defaults import *

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
