import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), r'backend\.venv\Lib\site-packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_project.settings'
import django; django.setup()
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from learning.views import LearningPathViewSet
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(role='INSTRUCTOR')
factory = RequestFactory()
req = factory.get('/api/paths/')
req.user = user
view = LearningPathViewSet.as_view({'get': 'list'})
resp = view(req)
print(f'Status: {resp.status_code}')
print(f'Count: {len(resp.data.get("results", []))}')
print(f'Has semester_id in first result: {"semester_id" in resp.data["results"][0] if resp.data.get("results") else "no results"}')
for r in resp.data.get('results', [])[:5]:
    print(f'  id={r["id"]} title={r["title"][:50]} sem_id={r.get("semester_id")}')
