from django.db import models
from django import forms
from django.contrib import admin

from django.contrib.auth.models import User

def generate_mp3_filename(instance, filename):
    import hashlib, datetime
    now = datetime.datetime.now().isoformat()
    return hashlib.sha1(now + filename).hexdigest() + '.mp3'

class MusicFile(models.Model):
    owner = models.ForeignKey(User)
    file = models.FileField(upload_to=generate_mp3_filename)
    file_name = models.CharField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'MusicFile "%s"' % self.file_name

admin.site.register(MusicFile)

class MusicFileForm(forms.ModelForm):
    class Meta:
        model = MusicFile
        fields = ['file']
