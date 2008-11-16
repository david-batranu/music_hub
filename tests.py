import unittest
import re

from django.test.client import Client
from django.contrib.auth.models import User
from models import MusicFile, get_disk_usage

def make_file(name, data):
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
        self.failUnless('File' in response.content)
        self.failIf('Owner' in response.content)
        self.client.logout()
    
    def test_one_upload(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.post('/upload', {'file': make_file('music.mp3', '..data..')})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('success' in response.content)
        f = MusicFile.objects.get()
        self.failUnless(f.file.name.endswith('.mp3'))
        self.failUnlessEqual(f.file_name, 'music.mp3')
        self.failUnless(f.owner == self.gigel)
        self.client.logout()
    
    def test_without_user(self):
        response = self.client.post('/upload', {'file': make_file('music.mp3', '..data..')})
        self.failIf('success' in response.content)
        self.failUnless('log in' in response.content)
        response = self.client.get('/upload')
        self.failUnless('log in' in response.content)
    
    def test_remove_file(self):
        # upload the file
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'file': make_file('music.mp3', '..data..')})
        self.failUnlessEqual(MusicFile.objects.filter(file_name='music.mp3').count(), 1)
        self.client.logout()
        
        # bad request (GET)
        response = self.client.get('/delete')
        self.failUnlessEqual(response.status_code, 405)
        
        # no such file
        response = self.client.post('/delete')
        self.failUnlessEqual(response.status_code, 400)
        self.failUnless('The file does not exist' in response.content)
        response = self.client.post('/delete', {'file': 13})
        self.failUnlessEqual(response.status_code, 400)
        self.failUnless('The file does not exist' in response.content)
        
        # bad user
        response = self.client.post('/delete', {'file': MusicFile.objects.get(file_name='music.mp3').id})
        self.failUnlessEqual(response.status_code, 403)
        self.failUnless('This file is not yours to delete' in response.content)
        
        # the correct request
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/delete', {'file': MusicFile.objects.get(file_name='music.mp3').id})
        self.failUnlessEqual(MusicFile.objects.filter(file_name='music.mp3').count(), 0)
        self.client.logout()
    
    def test_file_listing(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'file': make_file('music1.mp3', '..data..')})
        self.client.post('/upload', {'file': make_file('music2.mp3', '..data..')})
        self.client.post('/upload', {'file': make_file('music3.mp3', '..data..')})
        response = self.client.get('/list/gigel')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('music1.mp3' in response.content)
        self.failUnless('music2.mp3' in response.content)
        self.failUnless('music3.mp3' in response.content)
        self.client.logout()
    
    def test_get_file(self):
        # upload the file
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'file': make_file('music1.mp3', '..data..')})
        self.client.logout()
        file_code = MusicFile.objects.get(file_name='music1.mp3').file.name[:-4]
        
        # bad user
        response = self.client.get('/file/%s' % file_code)
        self.failUnlessEqual(response.status_code, 403)
        response = self.client.get('/file/%s/download' % file_code)
        self.failUnlessEqual(response.status_code, 403)
        
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        
        # no such file
        response = self.client.get('/file/a7c22186f41799f76f0a2534794543e5ac555eae')
        self.failUnlessEqual(response.status_code, 404)
        response = self.client.get('/file/a7c22186f41799f76f0a2534794543e5ac555eae/download')
        self.failUnlessEqual(response.status_code, 404)
        
        # correct request
        response = self.client.get('/file/%s' % file_code)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response['Content-Type'], 'text/html; charset=utf-8')
        self.failUnless('music1.mp3', response.content)
        response = self.client.get('/file/%s/download' % file_code)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response['Content-Disposition'], 'attachment; filename=music1.mp3')
        self.failUnlessEqual(response['Content-Length'], '8')
        self.failUnlessEqual(response.content, '..data..')
        
        self.client.logout()
    
    def test_absolute_url(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'file': make_file('music1.mp3', '..data..')})
        music_file = MusicFile.objects.get(file_name='music1.mp3')
        self.failUnlessEqual(music_file.get_absolute_url(), '/file/%s' % music_file.file.name[:-4])

class OtherPagesTest(MusicHubTestCase):
    def test_index(self):
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('Music hub' in response.content)
        self.failUnless('Latest uploads' in response.content)
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        for n in range(15):
            self.client.post('/upload', {'file': make_file('music%d.mp3' % n, '..data..')})
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
        for n in range(5):
            self.failUnless('music%d.mp3' % n not in response.content, 'music file %d should not be here' % n)
        for n in range(5,15):
            self.failUnless('music%d.mp3' % n in response.content, 'music file %d is missing' % n)
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

class LogFileTest(MusicHubTestCase):
    def test_file_upload_download_delete(self):
        # TODO: test encoding of non-ascii characters
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        # upload
        self.client.post('/upload', {'file': make_file('music1.mp3', '..data..')})
        file_code = MusicFile.objects.get(file_name='music1.mp3').file.name[:-4]
        self.failUnlessEqual(len(self.events), 1)
        event = self.events[0]
        self.failUnlessEqual(event['kind'], 'upload')
        self.failUnlessEqual(event['user'], 'gigel (%d)' % self.gigel.id)
        self.failUnlessEqual(event['ip'], '127.0.0.1')
        self.failUnless('original_filename: music1.mp3' in event['txt'])
        self.failUnless('hashed_filename: %s.mp3' % file_code in event['txt'])
        self.client.logout()
        
        # download
        self.failUnless(self.client.login(username='gigel2', password='gigi'))
        self.client.get('/file/%s' % file_code)
        self.failUnlessEqual(len(self.events), 1)
        self.client.get('/file/%s/download' % file_code)
        self.failUnlessEqual(len(self.events), 2)
        event = self.events[1]
        self.failUnlessEqual(event['kind'], 'download')
        self.failUnlessEqual(event['user'], 'gigel2 (%d)' % self.gigel2.id)
        self.failUnlessEqual(event['ip'], '127.0.0.1')
        self.failUnless('music1.mp3' in event['txt'])
        self.failUnless('hashed_filename: %s.mp3' % file_code in event['txt'])
        self.client.logout()
        
        # delete
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/delete', {'file': MusicFile.objects.get(file_name='music1.mp3').id})
        self.failUnlessEqual(len(self.events), 3)
        event = self.events[2]
        self.failUnlessEqual(event['kind'], 'delete')
        self.failUnlessEqual(event['user'], 'gigel (%d)' % self.gigel.id)
        self.failUnlessEqual(event['ip'], '127.0.0.1')
        self.failUnless('music1.mp3' in event['txt'])
        self.failUnless('hashed_filename: %s.mp3' % file_code in event['txt'])
        self.client.logout()

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
        response = self.client.post('/upload', {'file': make_file('music1.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(get_disk_usage(self.gigel), 10)
        self.failUnlessEqual(get_disk_usage(self.gigel2), 0)
        self.failUnlessEqual(get_disk_usage(), 10)
        self.failUnless(self.client.login(username='gigel2', password='gigi'))
        response = self.client.post('/upload', {'file': make_file('music2.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(get_disk_usage(self.gigel), 10)
        self.failUnlessEqual(get_disk_usage(self.gigel2), 10)
        self.failUnlessEqual(get_disk_usage(), 20)
    
    def test_user_quota(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.post('/upload', {'file': make_file('music1.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/upload', {'file': make_file('music2.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/upload', {'file': make_file('music3.mp3', '.' * 10)})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/upload', {'file': make_file('music4.mp3', '.' * 1)})
        self.failUnlessEqual(response.status_code, 400)
        self.failUnless('File upload failed: you have exceeded your quota' in response.content)
    
    def test_total_quota(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        response = self.client.post('/upload', {'file': make_file('music1.mp3', '.' * 25)})
        self.failUnlessEqual(response.status_code, 200)
        self.client.logout()
        self.failUnless(self.client.login(username='gigel2', password='gigi'))
        response = self.client.post('/upload', {'file': make_file('music2.mp3', '.' * 25)})
        self.failUnlessEqual(response.status_code, 500)
        self.failUnless('File upload failed: there is no more room on the server' in response.content)
