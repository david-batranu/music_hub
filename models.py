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
    """ return total size of songs owned by user (or all songs, if user is None) """
    
    # TODO: optimisation: do a raw SQL query
    if user:
        songs = Song.objects.filter(owner=user)
    else:
        songs = Song.objects.all()
    
    return sum(song.data_file.size for song in songs)

class QuotaError(ValueError):
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

class Song(models.Model):
    owner = models.ForeignKey(User)
    data_file = models.FileField(upload_to=generate_mp3_filename)
    original_name = models.CharField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def save(self):
        if get_disk_usage(self.owner) + self.data_file.size > USER_QUOTA:
            raise QuotaError('user', USER_QUOTA)
        if get_disk_usage() + self.data_file.size > TOTAL_QUOTA:
            raise QuotaError('total', USER_QUOTA)
        super(Song, self).save()
    
    @models.permalink
    def get_absolute_url(self):
        return ('music_hub.views.song_page', (), {'song_code': self.data_file.name[:-4]})
    
    @models.permalink
    def get_download_url(self):
        return ('music_hub.views.download_song', (), {'song_code': self.data_file.name[:-4]})
    
    def __unicode__(self):
        return u'Song "%s"' % self.original_name

admin.site.register(Song)

class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['data_file']
