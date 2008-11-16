from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def person_link(person):
    return render_to_string('tag_person_link.html', {'person': person, 'show_name': True})

@register.simple_tag
def person_link_with_name(person):
    return render_to_string('tag_person_link.html', {'person': person, 'show_name': False})

@register.simple_tag
def song_link(song, current_user=None):
    return render_to_string('tag_song_link.html', {
        'song': song,
        'can_delete': current_user and current_user == song.owner,
    })
