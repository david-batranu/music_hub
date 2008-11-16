from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    RenameField('MusicFile', 'file_name', 'original_name'),
]
