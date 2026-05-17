import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), r'backend\.venv\Lib\site-packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_project.settings'
import django; django.setup()
from learning.models import Semester
from learning.serializers import SemesterSerializer
qs = Semester.objects.filter(program_id=7)
for s in qs:
    ser = SemesterSerializer(instance=s)
    d = ser.data
    print(f'id={d["id"]} program={d["program"]} name={d["name"]}')
    print(f'  type(program)={type(d["program"]).__name__}')
