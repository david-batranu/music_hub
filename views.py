from django.shortcuts import render_to_response
from django.core.files.uploadedfile import SimpleUploadedFile

from models import MusicFileForm

def upload(request):
    if request.method == 'POST':
        form = MusicFileForm(request.POST, request.FILES)
        if form.is_valid():
            music_file = form.save(commit=False)
            music_file.owner = request.user
            music_file.save()
            return render_to_response('file_upload_done.html', {})
    else:
        form = MusicFileForm()
    
    return render_to_response('file_upload.html', {'form': form})
