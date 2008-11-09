from django.shortcuts import render_to_response, get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

from models import MusicFile, MusicFileForm

def upload(request):
    if isinstance(request.user, AnonymousUser):
        return render_to_response('error.html', {'message': "You need to log in."})
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

def delete(request):
    if request.method != 'POST':
        return render_to_response('error.html', {'message': "How did you get here? Only POST requests are allowed."})
    
    music_file_id = request.POST.get('file', '-1')
    
    try:
        music_file = MusicFile.objects.get(id=music_file_id)
    except ObjectDoesNotExist:
        return render_to_response('error.html', {'message': "How did you get here? The file does not exist."})
    
    if music_file.owner != request.user:
        return render_to_response('error.html', {'message': "How did you get here? This file is not yours to delete."})
    
    music_file.delete()
    return render_to_response('file_delete_done.html')

def file_listing(request, username):
    user = get_object_or_404(User, username=username)
    files = MusicFile.objects.filter(owner=user)
    return render_to_response('file_list.html', {'files': files})
