from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^upload$', 'music_hub.views.upload'),
    (r'^files/(?P<username>[^/]+)', 'music_hub.views.file_listing'),
    
    (r'^admin/(.*)', admin.site.root),
)
