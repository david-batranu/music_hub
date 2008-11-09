from django.shortcuts import render_to_response, get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from models import MusicFile, MusicFileForm

def upload(request):
    if request.method == 'POST':
        form = MusicFileForm(request.POST, request.FILES)
        if form.is_valid():
            music_file = form.save(commit=False)
            music_file.owner = request.user
            music_file.file_name = request.FILES['file'].name
            music_file.save()
            return render_to_response('file_upload_done.html', {})
    else:
        form = MusicFileForm()
    
    return render_to_response('file_upload.html', {'form': form})

def file_listing(request, username):
    user = get_object_or_404(User, username=username)
    files = MusicFile.objects.filter(owner=user)
    return render_to_response('file_list.html', {'files': files})
