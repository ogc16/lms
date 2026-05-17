import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), r'backend\.venv\Lib\site-packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_project.settings'
import django; django.setup()
from rest_framework.test import APIRequestFactory
from django.test import override_settings
from learning.views import SemesterViewSet
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(role='INSTRUCTOR')
factory = APIRequestFactory()
req = factory.get('/api/semesters/')
req.user = user
view = SemesterViewSet.as_view({'get': 'list'})
resp = view(req)
data = resp.data
print(f'Status: {resp.status_code}')
print(f'Type: {type(data).__name__}')
print(f'Count: {len(data)}')
for s in data:
    print(f'  id={s["id"]} program={s["program"]} (type={type(s["program"]).__name__}) name={s["name"]}')
