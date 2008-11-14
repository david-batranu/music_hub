from django_evolution.mutations import *
from django.db import models
from datetime import datetime

now = datetime.now()

MUTATIONS = [
    AddField('MusicFile', 'date_modified', models.DateTimeField, initial=now),
    AddField('MusicFile', 'date_created', models.DateTimeField, initial=now),
]