import unittest
import re

from django.test.client import Client
from django.contrib.auth.models import User
from models import MusicFile

def make_file(name, data):
    from StringIO import StringIO
    f = StringIO(data)
    f.name = name
    return f

class SingleFileTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.gigel = User.objects.create_user('gigel', 'gigel@example.com', 'gigi')
    
    def tearDown(self):
        self.gigel.delete()
    
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
        
        # bad user
        file_code = MusicFile.objects.get(file_name='music1.mp3').file.name[:-4]
        response = self.client.get('/files/%s' % file_code)
        self.failUnlessEqual(response.status_code, 403)
        
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        
        # no such file
        response = self.client.get('/files/a7c22186f41799f76f0a2534794543e5ac555eae')
        self.failUnlessEqual(response.status_code, 404)
        
        # correct request
        response = self.client.get('/files/%s' % file_code)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response['Content-Disposition'], 'attachment; filename=music1.mp3')
        self.failUnlessEqual(response['Content-Length'], '8')
        self.failUnlessEqual(response.content, '..data..')
        
        self.client.logout()

class OtherPagesTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.gigel = User.objects.create_user('gigel', 'gigel@example.com', 'gigi')
    
    def tearDown(self):
        self.gigel.delete()
    
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

class LogFileTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.gigel = User.objects.create_user('gigel', 'gigel@example.com', 'gigi')
        
        import log
        self.original_log = log.log_event
        self.events = []
        log.log_event = lambda kind, user, txt: self.events.append(
            {'kind': kind, 'user': user, 'txt': txt})
    
    def tearDown(self):
        self.gigel.delete()
        import log
        log.log_event = self.original_log
    
    def test_file_upload_delete(self):
        # TODO: test encoding of non-ascii characters
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'file': make_file('music1.mp3', '..data..')})
        self.failUnlessEqual(len(self.events), 1)
        self.failUnlessEqual(self.events[0]['kind'], 'upload')
        self.failUnlessEqual(self.events[0]['user'], 'gigel (%d)' % self.gigel.id)
        self.failUnless('original_filename: music1.mp3' in self.events[0]['txt'])
        self.failUnless(re.search(r'hashed_filename\: [0-9a-f]{40}\.mp3', self.events[0]['txt']))
        self.client.post('/delete', {'file': MusicFile.objects.get(file_name='music1.mp3').id})
        self.failUnlessEqual(len(self.events), 2)
        self.failUnlessEqual(self.events[1]['kind'], 'delete')
        self.failUnlessEqual(self.events[1]['user'], 'gigel (%d)' % self.gigel.id)
        self.failUnless('music1.mp3' in self.events[1]['txt'])
        self.failUnless(re.search(r'hashed_filename\: [0-9a-f]{40}\.mp3', self.events[1]['txt']))
        self.client.logout()
