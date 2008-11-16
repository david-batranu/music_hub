from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse, HttpResponseServerError, \
        HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest
from django.conf import settings

from models import MusicFile, MusicFileForm, QuotaError
from log import log_file_upload, log_file_download, log_file_delete

def index(request):
    latest_uploads = MusicFile.objects.order_by('-date_created')[:10]
    return render_to_response('index.html', {
        'latest_uploads': latest_uploads,
    })

def upload(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseForbidden("You need to log in.")
    if request.method == 'POST':
        form = MusicFileForm(request.POST, request.FILES)
        if form.is_valid():
            music_file = form.save(commit=False)
            music_file.owner = request.user
            music_file.original_name = request.FILES['file'].name
            try:
                music_file.save()
            except QuotaError, e:
                if e.kind == 'user':
                    return HttpResponseBadRequest('File upload failed: you have '
                        'exceeded your quota of %d bytes.' % e.value)
                elif e.kind == 'total':
                    return HttpResponseServerError('File upload failed: there is '
                        'no more room on the server.')
            log_file_upload(request, music_file)
            return render_to_response('file_upload_done.html', {})
    else:
        form = MusicFileForm()
    
    return render_to_response('file_upload.html', {'form': form})

def delete(request):
    from django.core.exceptions import ObjectDoesNotExist
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    music_file_id = request.POST.get('file', '-1')
    
    try:
        music_file = MusicFile.objects.get(id=music_file_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("The file does not exist.")
    
    if music_file.owner != request.user:
        return HttpResponseForbidden('This file is not yours to delete.')
    
    log_file_delete(request, music_file)
    music_file.delete()
    return render_to_response('file_delete_done.html')

def file_listing(request, username):
    user = get_object_or_404(User, username=username)
    files = MusicFile.objects.filter(owner=user)
    return render_to_response('file_list.html', {'files': files})

def file_page(request, file_code):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseForbidden('Only logged-in users can download files.')
    
    music_file = get_object_or_404(MusicFile, file='%s.mp3' % file_code)
    return render_to_response('file_page.html', {'music_file': music_file})

def download_file(request, file_code):
    import os
    from django.core.servers.basehttp import FileWrapper
    if isinstance(request.user, AnonymousUser):
        return HttpResponseForbidden('Only logged-in users can download files.')
    
    music_file = get_object_or_404(MusicFile, file='%s.mp3' % file_code)
    log_file_download(request, music_file)
    
    file_path = '%s%s' % (settings.MEDIA_ROOT, music_file.file)
    wrapper = FileWrapper(file(file_path))
    
    response = HttpResponse(wrapper, content_type='audio/mpeg')
    response['Content-Disposition'] = 'attachment; filename=%s' % music_file.original_name
    response['Content-Length'] = os.path.getsize(file_path)
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
