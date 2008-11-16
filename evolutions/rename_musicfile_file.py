from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    RenameField('MusicFile', 'file', 'data_file'),
]
