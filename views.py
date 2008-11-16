from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse, HttpResponseServerError, \
        HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest
from django.conf import settings

from models import Song, SongForm, QuotaError
from log import log_song_upload, log_song_download, log_song_delete

def index(request):
    latest_uploads = Song.objects.order_by('-date_created')[:10]
    people = filter(
        lambda user: Song.objects.filter(owner=user).count(),
        User.objects.all())
    return render_to_response('index.html', {
        'latest_uploads': latest_uploads,
        'logged_in': not isinstance(request.user, AnonymousUser),
        'people': people,
    })

def upload(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseForbidden("You need to log in.")
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.owner = request.user
            song.original_name = request.FILES['data_file'].name
            try:
                song.save()
            except QuotaError, e:
                if e.kind == 'user':
                    return HttpResponseBadRequest('File upload failed: you have '
                        'exceeded your quota of %d bytes.' % e.value)
                elif e.kind == 'total':
                    return HttpResponseServerError('File upload failed: there is '
                        'no more room on the server.')
            log_song_upload(request, song)
            return render_to_response('song_upload_done.html', {})
    else:
        form = SongForm()
    
    return render_to_response('song_upload.html', {'form': form})

def delete(request):
    from django.core.exceptions import ObjectDoesNotExist
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    song_id = request.POST.get('song', '-1')
    
    try:
        song = Song.objects.get(id=song_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("The song does not exist.")
    
    if song.owner != request.user:
        return HttpResponseForbidden('This song is not yours to delete.')
    
    log_song_delete(request, song)
    song.delete()
    return render_to_response('song_delete_done.html')

def person_page(request, username):
    user = get_object_or_404(User, username=username)
    songs = Song.objects.filter(owner=user)
    return render_to_response('person_page.html', {'songs': songs})

def song_page(request, song_code):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseForbidden('Only logged-in users can download songs.')
    
    song = get_object_or_404(Song, data_file='%s.mp3' % song_code)
    return render_to_response('song_page.html', {'song': song})

def download_song(request, song_code):
    import os
    from django.core.servers.basehttp import FileWrapper
    if isinstance(request.user, AnonymousUser):
        return HttpResponseForbidden('Only logged-in users can download songs.')
    
    song = get_object_or_404(Song, data_file='%s.mp3' % song_code)
    log_song_download(request, song)
    
    data_file_path = '%s%s' % (settings.MEDIA_ROOT, song.data_file)
    wrapper = FileWrapper(file(data_file_path))
    
    response = HttpResponse(wrapper, content_type='audio/mpeg')
    response['Content-Disposition'] = 'attachment; filename=%s' % song.original_name
    response['Content-Length'] = os.path.getsize(data_file_path)
    return response

def auth(request):
    from django.contrib.auth.forms import AuthenticationForm
    from django.contrib.auth import login, logout
    
    if isinstance(request.user, AnonymousUser):
        if request.method == 'POST':
            if request.POST.get('do', None) != 'login':
                return HttpResponseBadRequest('Logged-in users can only perform logout.')
            
            auth_form = AuthenticationForm(request, request.POST)
            if auth_form.is_valid():
                login(request, auth_form.get_user())
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                return render_to_response('auth_logged_in.html', {'user': request.user})
        
        else:
            auth_form = AuthenticationForm()
        
        request.session.set_test_cookie()
        return render_to_response('auth_login.html', {'auth_form': auth_form})
    
    else:
        if request.method == 'POST':
            if request.POST.get('do', None) != 'logout':
                return HttpResponseBadRequest('Logged-in users can only perform logout.')
            
            logout(request)
            return render_to_response('auth_login.html', {'auth_form': AuthenticationForm()})
        
        else:
            return render_to_response('auth_logged_in.html', {'user': request.user})
