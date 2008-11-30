import unittest
import re

from django.test.client import Client
from django.contrib.auth.models import User
from models import Song, get_disk_usage

def make_song(name, data):
    from StringIO import StringIO
    f = StringIO(data)
    f.name = name
    return f

class MusicHubTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(REMOTE_ADDR='127.0.0.1')
        self.gigel = User.objects.create_user('gigel', 'gigel@example.com', 'gigi')
        self.gigel2 = User.objects.create_user('gigel2', 'gigel2@example.com', 'gigi')
        
        import log
        self.original_log = log.log_event
        self.events = []
        log.log_event = lambda kind, user, ip, txt: self.events.append(
            {'kind': kind, 'user': user, 'ip': ip, 'txt': txt})
    
    def tearDown(self):
        self.gigel.delete()
        self.gigel2.delete()
        
        import log
        log.log_event = self.original_log

class SingleFileTest(MusicHubTestCase):
    def test_upload_form(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.get('/upload')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('Data file' in response.content)
        self.failIf('Owner' in response.content)
    
    def test_one_upload(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.post('/upload', {'data_file': make_song('music.mp3', '..data..')})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('success' in response.content)
        f = Song.objects.get()
        self.failUnless(f.data_file.name.endswith('.mp3'))
        self.failUnlessEqual(f.original_name, 'music.mp3')
        self.failUnless(f.owner == self.gigel)
    
    def test_without_user(self):
        response = self.client.post('/upload', {'data_file': make_song('music.mp3', '..data..')})
        self.failIf('success' in response.content)
        self.failUnless('log in' in response.content)
        response = self.client.get('/upload')
        self.failUnless('log in' in response.content)
    
    def test_remove_song(self):
        # upload the song
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'data_file': make_song('music.mp3', '..data..')})
        self.failUnlessEqual(Song.objects.filter(original_name='music.mp3').count(), 1)
        self.client.logout()
        
        # bad request (GET)
        response = self.client.get('/delete')
        self.failUnlessEqual(response.status_code, 405)
        
        # no such song
        response = self.client.post('/delete')
        self.failUnlessEqual(response.status_code, 400)
        self.failUnless('The song does not exist' in response.content)
        response = self.client.post('/delete', {'song': 13})
        self.failUnlessEqual(response.status_code, 400)
        self.failUnless('The song does not exist' in response.content)
        
        # bad user
        response = self.client.post('/delete', {'song': Song.objects.get(original_name='music.mp3').id})
        self.failUnlessEqual(response.status_code, 403)
        self.failUnless('This song is not yours to delete' in response.content)
        
        # the correct request
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/delete', {'song': Song.objects.get(original_name='music.mp3').id})
        self.failUnlessEqual(Song.objects.filter(original_name='music.mp3').count(), 0)
    
    def test_song_listing(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'data_file': make_song('music1.mp3', '..data..')})
        self.client.post('/upload', {'data_file': make_song('music2.mp3', '..data..')})
        self.client.post('/upload', {'data_file': make_song('music3.mp3', '..data..')})
        response = self.client.get('/people/gigel')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('music1.mp3' in response.content)
        self.failUnless('music2.mp3' in response.content)
        self.failUnless('music3.mp3' in response.content)
    
    def test_get_song(self):
        # upload the song
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'data_file': make_song('music 1.mp3', '..data..')})
        self.client.logout()
        song_code = Song.objects.get(original_name='music 1.mp3').get_code()
        
        # bad user
        response = self.client.get('/song/%s' % song_code)
        self.failUnlessEqual(response.status_code, 403)
        response = self.client.get('/song/%s/download' % song_code)
        self.failUnlessEqual(response.status_code, 403)
        
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        
        # no such song
        response = self.client.get('/song/a7c22186f41799f76f0a2534794543e5ac555eae')
        self.failUnlessEqual(response.status_code, 404)
        response = self.client.get('/song/a7c22186f41799f76f0a2534794543e5ac555eae/download')
        self.failUnlessEqual(response.status_code, 404)
        
        # correct request
        response = self.client.get('/song/%s' % song_code)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response['Content-Type'], 'text/html; charset=utf-8')
        self.failUnless('music 1.mp3', response.content)
        response = self.client.get('/song/%s/download' % song_code)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response['Content-Disposition'], 'attachment; filename=music%201.mp3')
        self.failUnlessEqual(response['Content-Length'], '8')
        self.failUnlessEqual(response.content, '..data..')
    
    def test_big_song_download(self):
        size = 1024*1024*3 # 3 MB
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'data_file': make_song('music1.mp3', '.' * size)})
        response = self.client.get(Song.objects.get(original_name='music1.mp3').get_download_url())
        self.failUnlessEqual(response['Content-Length'], str(size))
        self.failUnlessEqual(len(response.content), size)

class SongObjectTest(MusicHubTestCase):
    def setUp(self):
        super(SongObjectTest, self).setUp()
        self.client.login(username='gigel', password='gigi')
        self.client.post('/upload', {'data_file': make_song('music1.mp3', '..data..')})
        self.client.logout()
        self.song = Song.objects.get(original_name='music1.mp3')
    
    def test_get_code(self):
        self.failUnlessEqual(self.song.get_code(), self.song.data_file.name[:-4])
    
    def test_urls(self):
        self.failUnlessEqual(self.song.get_absolute_url(), '/song/%s' % self.song.get_code())
        self.failUnlessEqual(self.song.get_download_url(), '/song/%s/download' % self.song.get_code())

class OtherPagesTest(MusicHubTestCase):
    def test_index(self):
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('Music hub' in response.content)
        self.failUnless('Latest uploads' in response.content)
        self.failUnless('<a href="/auth"' in response.content)
        self.failIf('/upload' in response.content, 'the user must log in before he sees the "upload" link')
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.get('/')
        self.failUnless('<a href="/upload"' in response.content)
        for n in range(15):
            self.client.post('/upload', {'data_file': make_song('music%d.mp3' % n, '..data..')})
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
        for n in range(5):
            self.failUnless('music%d.mp3' % n not in response.content, 'song %d should not be here' % n)
        for n in range(5,15):
            self.failUnless('music%d.mp3' % n in response.content, 'song %d is missing' % n)
        self.failUnless('gigel' in response.content)
    
    def test_404(self):
        response = self.client.get('/no_such_file')
        self.failUnlessEqual(response.status_code, 404)
    
    def test_login(self):
        # login page
        response = self.client.get('/auth')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('Log in' in response.content)
        self.failUnless('<form' in response.content)
        
        # submit login (bad user)
        response = self.client.post('/auth', {'do': 'login', 'username': 'bebe', 'password': '123'})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('Please enter a correct username and password' in response.content)
        
        # submit login (good user)
        response = self.client.post('/auth', {'do': 'login', 'username': 'gigel', 'password': 'gigi'})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('You are logged in as gigel' in self.client.get('/auth').content)
    
    def test_logout(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        
        # check auth page
        response = self.client.get('/auth')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('You are logged in as gigel' in self.client.get('/auth').content)
        
        # check log out
        response = self.client.post('/auth', {'do': 'logout'})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('Log in' in response.content)
        self.failUnless('<form' in response.content)
    
    def test_song_page(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'data_file': make_song('music1.mp3', '..data..')})
        song = Song.objects.get(original_name='music1.mp3')
        response = self.client.get(song.get_absolute_url())
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(song.owner.username in response.content)
        self.failUnless(song.original_name in response.content)
        self.failUnless(song.get_download_url() in response.content)

class LogFileTest(MusicHubTestCase):
    def test_song_upload_download_delete(self):
        # TODO: test encoding of non-ascii characters
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        # upload
        self.client.post('/upload', {'data_file': make_song('music1.mp3', '..data..')})
        song_code = Song.objects.get(original_name='music1.mp3').get_code()
        self.failUnlessEqual(len(self.events), 1)
        event = self.events[0]
        self.client.logout()
        self.failUnlessEqual(event['kind'], 'upload')
        self.failUnlessEqual(event['user'], 'gigel (%d)' % self.gigel.id)
        self.failUnlessEqual(event['ip'], '127.0.0.1')
        self.failUnless('original_filename: music1.mp3' in event['txt'])
        self.failUnless('code: %s' % song_code in event['txt'])
        self.failUnless('file_size: 8' in event['txt'])
        
        # download
        self.failUnless(self.client.login(username='gigel2', password='gigi'))
        self.client.get('/song/%s' % song_code)
        self.failUnlessEqual(len(self.events), 1)
        self.client.get('/song/%s/download' % song_code)
        self.failUnlessEqual(len(self.events), 2)
        self.client.logout()
        event = self.events[1]
        self.failUnlessEqual(event['kind'], 'download')
        self.failUnlessEqual(event['user'], 'gigel2 (%d)' % self.gigel2.id)
        self.failUnlessEqual(event['ip'], '127.0.0.1')
        self.failUnless('music1.mp3' in event['txt'])
        self.failUnless('code: %s' % song_code in event['txt'])
        self.failUnless('file_size: 8' in event['txt'])
        
        # delete
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/delete', {'song': Song.objects.get(original_name='music1.mp3').id})
        self.failUnlessEqual(len(self.events), 3)
        self.client.logout()
        event = self.events[2]
        self.failUnlessEqual(event['kind'], 'delete')
        self.failUnlessEqual(event['user'], 'gigel (%d)' % self.gigel.id)
        self.failUnlessEqual(event['ip'], '127.0.0.1')
        self.failUnless('music1.mp3' in event['txt'])
        self.failUnless('code: %s' % song_code in event['txt'])
        self.failUnless('file_size: 8' in event['txt'])
    
    def test_proxy_ip(self):
        client2 = Client(REMOTE_ADDR='127.0.0.1', HTTP_X_FORWARDED_FOR='1.2.3.4')
        self.failUnless(client2.login(username='gigel', password='gigi'))
        client2.post('/upload', {'data_file': make_song('music1.mp3', '..data..')})
        song_code = Song.objects.get(original_name='music1.mp3').get_code()
        event = self.events[0]
        self.failUnlessEqual(event['ip'], '1.2.3.4')

class QuotaTest(MusicHubTestCase):
    def setUp(self):
        super(QuotaTest, self).setUp()
        import models
        self.orig_quota = (models.USER_QUOTA, models.TOTAL_QUOTA)
        models.USER_QUOTA = 30
        models.TOTAL_QUOTA = 40
    
    def tearDown(self):
        import models
        (models.USER_QUOTA, models.TOTAL_QUOTA) = self.orig_quota
        super(QuotaTest, self).tearDown()
    
    def test_get_disk_usage(self):
        self.failUnlessEqual(get_disk_usage(self.gigel), 0)
        self.failUnlessEqual(get_disk_usage(self.gigel2), 0)
        self.failUnlessEqual(get_disk_usage(), 0)
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.post('/upload', {'data_file': make_song('music1.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(get_disk_usage(self.gigel), 10)
        self.failUnlessEqual(get_disk_usage(self.gigel2), 0)
        self.failUnlessEqual(get_disk_usage(), 10)
        self.failUnless(self.client.login(username='gigel2', password='gigi'))
        response = self.client.post('/upload', {'data_file': make_song('music2.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(get_disk_usage(self.gigel), 10)
        self.failUnlessEqual(get_disk_usage(self.gigel2), 10)
        self.failUnlessEqual(get_disk_usage(), 20)
    
    def test_user_quota(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.post('/upload', {'data_file': make_song('music1.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/upload', {'data_file': make_song('music2.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/upload', {'data_file': make_song('music3.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/upload', {'data_file': make_song('music4.mp3', '.' * 1)})
        self.failUnlessEqual(response.status_code, 400)
        self.failUnless('File upload failed: you have exceeded your quota' in response.content)
    
    def test_total_quota(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.post('/upload', {'data_file': make_song('music1.mp3', '.' * 25)})
        self.failUnlessEqual(response.status_code, 200)
        self.client.logout()
        self.failUnless(self.client.login(username='gigel2', password='gigi'))
        response = self.client.post('/upload', {'data_file': make_song('music2.mp3', '.' * 25)})
        self.failUnlessEqual(response.status_code, 500)
        self.failUnless('File upload failed: there is no more room on the server' in response.content)
