from django.db import models
from django import forms
from django.contrib import admin
from django.conf import settings

from django.contrib.auth.models import User

USER_QUOTA = settings.MUSIC_HUB_USER_QUOTA
TOTAL_QUOTA = settings.MUSIC_HUB_TOTAL_QUOTA

def generate_mp3_filename(instance, filename):
    import hashlib, datetime
    now = datetime.datetime.now().isoformat()
    return hashlib.sha1(now + filename).hexdigest() + '.mp3'

def get_disk_usage(user=None):
    """ return total size of files owned by user (or all files, if user is None) """
    
    # TODO: optimisation: do a raw SQL query
    if user:
        files = MusicFile.objects.filter(owner=user)
    else:
        files = MusicFile.objects.all()
    
    return sum(music_file.file.size for music_file in files)

class QuotaError(ValueError):
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

class MusicFile(models.Model):
    owner = models.ForeignKey(User)
    file = models.FileField(upload_to=generate_mp3_filename)
    file_name = models.CharField(max_length=256) # TODO: rename to original_name
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def save(self):
        if get_disk_usage(self.owner) + self.file.size > USER_QUOTA:
            raise QuotaError('user', USER_QUOTA)
        if get_disk_usage() + self.file.size > TOTAL_QUOTA:
            raise QuotaError('total', USER_QUOTA)
        super(MusicFile, self).save()
    
    @models.permalink
    def get_absolute_url(self):
        return ('music_hub.views.file_page', (), {'file_code': self.file.name[:-4]})
    
    @models.permalink
    def get_download_url(self):
        return ('music_hub.views.download_file', (), {'file_code': self.file.name[:-4]})
    
    def __unicode__(self):
        return u'MusicFile "%s"' % self.file_name

admin.site.register(MusicFile)

class MusicFileForm(forms.ModelForm):
    class Meta:
        model = MusicFile
        fields = ['file']
