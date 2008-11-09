import unittest

from django.test.client import Client
from django.contrib.auth.models import User
from models import MusicFile

def make_file(name, data):
    from StringIO import StringIO
    f = StringIO(data)
    f.name = name
    return f

class FileUploadTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.gigel = User.objects.create_user('gigel', 'gigel@example.com', 'gigi')
    
    def tearDown(self):
        self.gigel.delete()
    
    def test_upload_form(self):
        response = self.client.get('/upload')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('File' in response.content)
        self.failIf('Owner' in response.content)
    
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
    
    def test_file_listing(self):
        self.failUnless(self.client.login(username='gigel', password='gigi'))
        self.client.post('/upload', {'file': make_file('music1.mp3', '..data..')})
        self.client.post('/upload', {'file': make_file('music2.mp3', '..data..')})
        self.client.post('/upload', {'file': make_file('music3.mp3', '..data..')})
        response = self.client.get('/files/gigel')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('music1.mp3' in response.content)
        self.failUnless('music2.mp3' in response.content)
        self.failUnless('music3.mp3' in response.content)
        MusicFile.objects.filter(owner=self.gigel).delete()
        self.client.logout()
