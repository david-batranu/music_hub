from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'music_hub.views.index'),
    (r'^upload$', 'music_hub.views.upload'),
    (r'^delete$', 'music_hub.views.delete'),
    (r'^list/(?P<username>[^/]+)$', 'music_hub.views.file_listing'),
    (r'^file/(?P<file_code>[0-9a-f]+)$', 'music_hub.views.file_page'),
    (r'^file/(?P<file_code>[0-9a-f]+)/download$', 'music_hub.views.download_file'),
    
    (r'^auth$', 'music_hub.views.auth'),
    
    (r'^admin/(.*)', admin.site.root),
)
