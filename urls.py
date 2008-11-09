from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^upload$', 'music_hub.views.upload'),
    (r'^delete$', 'music_hub.views.delete'),
    (r'^list/(?P<username>[^/]+)$', 'music_hub.views.file_listing'),
    (r'^files/(?P<file_code>[0-9a-f]+)$', 'music_hub.views.get_file'),
    
    (r'^admin/(.*)', admin.site.root),
)
