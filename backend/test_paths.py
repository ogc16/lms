import os, sys, json
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_project.settings'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django
django.setup()
from django.test import Client

c = Client(HTTP_HOST='localhost')

# Login
resp = c.post('/api/auth/login/', json.dumps({'email': 'wap@gmail.com', 'password': 'pass'}),
              content_type='application/json')
data = json.loads(resp.content)
token = data.get('token', '')
print(f'Login status: {resp.status_code}, token: {bool(token)}')

# Hit paths endpoint with auth header
resp = c.get('/api/paths/', HTTP_AUTHORIZATION=f'Bearer {token}')
print(f'Paths status: {resp.status_code}')
print(f'Paths body: {resp.content.decode()[:500]}')
