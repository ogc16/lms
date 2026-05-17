import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), r'backend\.venv\Lib\site-packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_project.settings'
import django
django.setup()
from django.db import transaction
from learning.models import LearningPath, Module, Lesson, Question

instructor_id = 1

def mk_mod(path, title, sort):
    return Module.objects.create(learning_path=path, title=title, description='', sort_order=sort)
def mk_les(mod, title, sort):
    return Lesson.objects.create(module=mod, title=title, description='', content_type=Lesson.ContentType.MARKDOWN, content_body='', duration_minutes=10, status=Lesson.Status.PUBLISHED, sort_order=sort)
def mk_qz(mod, title, sort, questions):
    les = Lesson.objects.create(module=mod, title=title, description='', content_type=Lesson.ContentType.QUIZ, content_body='', duration_minutes=5, status=Lesson.Status.PUBLISHED, sort_order=sort)
    for i, q in enumerate(questions):
        Question.objects.create(lesson=les, question_text=q['q'], option_a=q['a'], option_b=q['b'], option_c=q['c'], option_d=q['d'], correct_option=q['k'], sort_order=i+1)

def make_path(title, desc, topics, proj_steps, quiz_pool, diff):
    p = LearningPath.objects.create(title=title, description=desc, status=LearningPath.Status.PUBLISHED, difficulty=diff, estimated_hours=0, instructor_id=instructor_id)
    for i, t in enumerate(topics, 1):
        mod = mk_mod(p, t, i)
        mk_les(mod, f'Introduction to {t}', 1)
        mk_les(mod, f'Core Concepts in {t}', 2)
        mk_les(mod, f'Practical {t} Techniques', 3)
        mk_les(mod, f'{t} Best Practices', 4)
        mk_qz(mod, f'{t} Quiz', 5, quiz_pool)
    mod = mk_mod(p, f'Project: {title}', len(topics)+1)
    for j, s in enumerate(proj_steps, 1):
        mk_les(mod, s, j)
    mk_qz(mod, f'{title} Project Quiz', len(proj_steps)+1, quiz_pool)
    p.estimated_hours = round((len(topics)*(4*10+5) + (len(proj_steps)*10+5))/60)
    p.save(update_fields=['estimated_hours'])
    print(f'  Created: {p.title} (id={p.id})')
    return p

Q_FE = [
    {'q':'Which HTML tag creates a hyperlink?','a':'<link>','b':'<a>','c':'<href>','d':'<url>','k':'b'},
    {'q':'What does the CSS property display: flex do?','a':'Hides the element','b':'Creates a flex container','c':'Adds padding','d':'Changes font size','k':'b'},
    {'q':'Which React hook is used for side effects?','a':'useState','b':'useEffect','c':'useContext','d':'useReducer','k':'b'},
    {'q':'What is the purpose of TypeScript?','a':'Adds static typing to JavaScript','b':'Compiles CSS','c':'Manages state','d':'Creates databases','k':'a'},
    {'q':'What does responsive design mean?','a':'Fast loading pages','b':'Design adapts to different screen sizes','c':'Animated elements','d':'Server-side rendering','k':'b'},
    {'q':'Which tool bundles JavaScript modules?','a':'Node.js','b':'Webpack','c':'PostgreSQL','d':'Django','k':'b'},
    {'q':'What is the virtual DOM?','a':'A real DOM copy in memory','b':'A database cache','c':'A CSS framework','d':'A server-side template','k':'a'},
    {'q':'What does API stand for?','a':'Application Programming Interface','b':'Advanced Program Integration','c':'Automatic Protocol Interface','d':'Application Process Integration','k':'a'},
    {'q':'Which CSS unit is relative to viewport width?','a':'px','b':'em','c':'vw','d':'percent','k':'c'},
    {'q':'What does package.json define?','a':'Style definitions','b':'Project dependencies and scripts','c':'Database schema','d':'Build configuration','k':'b'},
]
Q_BE = [
    {'q':'What is a REST API?','a':'A database type','b':'An architectural style for APIs','c':'A CSS framework','d':'A Python library','k':'b'},
    {'q':'What does SQL stand for?','a':'Simple Query Language','b':'Structured Query Language','c':'Standard Query Logic','d':'Sequential Query Language','k':'b'},
    {'q':'Which HTTP method updates a resource?','a':'GET','b':'POST','c':'PUT','d':'DELETE','k':'c'},
    {'q':'What is an ORM?','a':'Object-Relational Mapping','b':'Online Request Manager','c':'Operating Resource Module','d':'Object Routing Model','k':'a'},
    {'q':'What is authentication?','a':'Verifying user identity','b':'Encrypting data','c':'Creating backups','d':'Optimising queries','k':'a'},
    {'q':'What does middleware do in web frameworks?','a':'Processes requests before they reach routes','b':'Creates databases','c':'Renders HTML','d':'Manages CSS','k':'a'},
    {'q':'What is a database migration?','a':'Moving data between servers','b':'Version-controlled schema changes','c':'Backing up data','d':'Indexing tables','k':'b'},
    {'q':'What does CSRF protect against?','a':'Cross-Site Request Forgery','b':'Database injection','c':'Password theft','d':'DNS spoofing','k':'a'},
    {'q':'Which status code means Not Found?','a':'200','b':'301','c':'404','d':'500','k':'c'},
    {'q':'What is caching used for?','a':'Storing frequently accessed data for faster retrieval','b':'Encrypting passwords','c':'Compressing images','d':'Creating backups','k':'a'},
]

with transaction.atomic():
    print('=== Frontend Development ===')
    make_path(
        'Frontend Development',
        'A comprehensive path covering modern frontend development: HTML, CSS, JavaScript, React, TypeScript, responsive design, and build tooling.',
        ['HTML5 and Semantic Markup','CSS3 and Modern Layouts','JavaScript ES6+','React Fundamentals','TypeScript','Frontend Build Tools','Responsive and Accessible Design'],
        ['Project Planning and Architecture','Component Library Setup','State Management Implementation','API Integration','Testing and Optimisation','Deployment and CI/CD'],
        Q_FE, LearningPath.Difficulty.INTERMEDIATE
    )

    print('=== Backend Development ===')
    make_path(
        'Backend Development',
        'Comprehensive backend engineering covering REST APIs, databases, authentication, server-side frameworks, caching, and deployment.',
        ['HTTP and RESTful APIs','SQL and Database Design','Python Backend (Django/DRF)','Authentication and Authorisation','API Security and Middleware','Database Migrations and ORM','Caching and Performance Optimisation'],
        ['Requirements Analysis','API Design and Documentation','Database Schema and Migrations','Authentication and Authorisation','Testing and Error Handling','Deployment and Monitoring'],
        Q_BE, LearningPath.Difficulty.INTERMEDIATE
    )

    print(f'\nPaths: {LearningPath.objects.count()}')
    print(f'Modules: {Module.objects.count()}')
    print(f'Lessons: {Lesson.objects.count()}')
