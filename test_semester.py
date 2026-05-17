import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), r'backend\.venv\Lib\site-packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_project.settings'
import django; django.setup()
from learning.models import LearningPath
from learning.serializers import LearningPathListSerializer

qs = LearningPath.objects.filter(semester_id=15).select_related('instructor')
for p in qs:
    ser = LearningPathListSerializer(instance=p)
    sid = ser.data.get('semester_id')
    sname = ser.data.get('semester_name')
    print(f'Path {p.id}: semester_id={sid!r} semester_name={sname!r}')
