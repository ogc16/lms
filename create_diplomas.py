import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), r'backend\.venv\Lib\site-packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_project.settings'

import django
django.setup()
from django.db import transaction
from django.contrib.auth import get_user_model
from learning.models import Program, Semester, LearningPath, Module, Lesson, Question

User = get_user_model()
instructor = User.objects.get(role='INSTRUCTOR', id=1)
DIR = LearningPath.Difficulty

def mk_mod(path, title, sort):
    return Module.objects.create(learning_path=path, title=title, description='', sort_order=sort)

def mk_les(mod, title, sort, duration=10):
    return Lesson.objects.create(module=mod, title=title, description='', content_type=Lesson.ContentType.MARKDOWN, content_body='', duration_minutes=duration, status=Lesson.Status.PUBLISHED, sort_order=sort)

def mk_qz(mod, title, sort, questions, dur=5):
    les = Lesson.objects.create(module=mod, title=title, description='', content_type=Lesson.ContentType.QUIZ, content_body='', duration_minutes=dur, status=Lesson.Status.PUBLISHED, sort_order=sort)
    for i, q in enumerate(questions):
        Question.objects.create(lesson=les, question_text=q['text'], option_a=q['a'], option_b=q['b'], option_c=q['c'], option_d=q['d'], correct_option=q['correct'], sort_order=i+1)
    return les

def cp(title, desc, modules_data, semester=None, difficulty=DIR.INTERMEDIATE):
    path = LearningPath.objects.create(title=title, description=desc, status=LearningPath.Status.PUBLISHED, difficulty=difficulty, estimated_hours=0, instructor=instructor, semester=semester)
    total_min = 0
    for i, md in enumerate(modules_data, 1):
        mod = mk_mod(path, md['title'], i)
        for j, lt in enumerate(md['lessons'], 1):
            mk_les(mod, lt, j, duration=md.get('duration', 10))
        if md.get('quiz'):
            mk_qz(mod, f"{md['title']} Quiz", len(md['lessons'])+1, md['quiz'])
            total_min += 5
    path.estimated_hours = round((total_min + sum(len(md['lessons']) * md.get('duration',10) for md in modules_data)) / 60)
    path.save(update_fields=['estimated_hours'])
    return path

def bm(topics, project_title, steps, pool):
    ms = []
    for t in topics:
        ms.append({'title': t, 'lessons': [f'Introduction to {t}', f'Core Concepts in {t}', f'Practical {t} Techniques', f'{t} Best Practices'], 'quiz': pool})
    ms.append({'title': f'Project: {project_title}', 'lessons': steps, 'quiz': pool})
    return ms

Q_IT = [
    {'text':'What does CPU stand for?','a':'Central Processing Unit','b':'Computer Personal Unit','c':'Central Program Utility','d':'Core Processing Unit','correct':'a'},
    {'text':'Which device connects a computer to a network?','a':'Monitor','b':'Network Interface Card','c':'Keyboard','d':'Printer','correct':'b'},
    {'text':'What is the function of an operating system?','a':'Run applications only','b':'Manage hardware and software resources','c':'Connect to the internet','d':'Edit documents','correct':'b'},
    {'text':'Which storage type is volatile?','a':'Hard disk','b':'RAM','c':'SSD','d':'USB drive','correct':'b'},
    {'text':'HTTP stands for:','a':'HyperText Transfer Protocol','b':'High Transfer Text Protocol','c':'HyperText Transmission Process','d':'High Tech Transfer Protocol','correct':'a'},
    {'text':'What is an IP address used for?','a':'Identifying a device on a network','b':'Storing passwords','c':'Encrypting data','d':'Managing files','correct':'a'},
    {'text':'Which of these is an input device?','a':'Monitor','b':'Keyboard','c':'Speaker','d':'Printer','correct':'b'},
    {'text':'Cloud computing delivers:','a':'Hardware only','b':'Computing services over the internet','c':'Local storage only','d':'Physical servers','correct':'b'},
    {'text':'What does DNS do?','a':'Detects network threats','b':'Resolves domain names to IP addresses','c':'Manages database queries','d':'Encrypts network traffic','correct':'b'},
    {'text':'The binary system uses base:','a':'2','b':'10','c':'8','d':'16','correct':'a'},
]
Q_BUS = [
    {'text':'What is the primary goal of a business?','a':'Maximise employee satisfaction','b':'Create and retain customers profitably','c':'Minimise costs','d':'Maximise production','correct':'b'},
    {'text':'SWOT analysis examines:','a':'Sales, Wages, Output, Tax','b':'Strengths, Weaknesses, Opportunities, Threats','c':'Strategy, Work, Organisation, Time','d':'System, Workflow, Output, Testing','correct':'b'},
    {'text':'What does PESTLE analysis cover?','a':'Product, Employee, Sales, Tax, Legal, Environment','b':'Political, Economic, Social, Technological, Legal, Environmental','c':'Planning, Execution, Staff, Training, Leadership, Ethics','d':'Price, Equity, Supply, Trade, Labour, Exchange','correct':'b'},
    {'text':'The four Ps of marketing are:','a':'Product, Price, Place, Promotion','b':'Planning, Production, Profit, People','c':'Price, Profit, Publicity, Packaging','d':'Product, People, Process, Physical','correct':'a'},
    {'text':'What is break-even analysis?','a':'Calculating total revenue','b':'Determining when revenue equals costs','c':'Measuring profit margins','d':'Analysing market share','correct':'b'},
    {'text':'A mission statement defines:','a':'Financial targets','b':'The purpose and core values of an organisation','c':'Employee performance goals','d':'Marketing strategy','correct':'b'},
    {'text':'Leadership is best described as:','a':'Managing budgets','b':'Influencing and guiding people towards goals','c':'Completing administrative tasks','d':'Monitoring employee performance','correct':'b'},
    {'text':'What is corporate social responsibility?','a':'Maximising shareholder returns','b':'Business commitment to ethical and sustainable practices','c':'Government regulation compliance','d':'Employee welfare programmes','correct':'b'},
    {'text':'Supply chain management involves:','a':'Marketing products','b':'Managing the flow of goods from suppliers to customers','c':'Employee recruitment','d':'Financial accounting','correct':'b'},
    {'text':'Benchmarking in business means:','a':'Setting financial targets','b':'Comparing performance against best practices','c':'Creating a budget','d':'Hiring consultants','correct':'b'},
]
Q_SE = [
    {'text':'What is the first phase of SDLC?','a':'Testing','b':'Requirements gathering','c':'Implementation','d':'Maintenance','correct':'b'},
    {'text':'Agile methodology emphasises:','a':'Comprehensive documentation','b':'Iterative development and customer collaboration','c':'Rigid planning','d':'Waterfall process','correct':'b'},
    {'text':'What is a version control system used for?','a':'Managing database schemas','b':'Tracking changes in source code','c':'Deploying applications','d':'Testing software','correct':'b'},
    {'text':'Unit testing tests:','a':'The entire system','b':'Individual components or functions','c':'User interface','d':'Network performance','correct':'b'},
    {'text':'What is technical debt?','a':'Money owed for software licenses','b':'Cost of rework from quick-and-dirty solutions','c':'Hardware depreciation','d':'Training costs','correct':'b'},
    {'text':'Which diagram is used for object-oriented design?','a':'Flowchart','b':'UML class diagram','c':'ER diagram','d':'Network diagram','correct':'b'},
    {'text':'The single responsibility principle means:','a':'A class should have only one reason to change','b':'A function should have one parameter','c':'A module should have one user','d':'A system should run on one server','correct':'a'},
    {'text':'What is continuous integration?','a':'Integrating databases','b':'Regularly merging code changes into a shared repository','c':'Continuous network connection','d':'Ongoing user training','correct':'b'},
    {'text':'A user story is:','a':'A technical specification','b':'A short description of a feature from user perspective','c':'A test case','d':'A deployment plan','correct':'b'},
    {'text':'What is refactoring?','a':'Adding new features','b':'Restructuring code without changing external behaviour','c':'Deleting old code','d':'Rewriting from scratch','correct':'b'},
]
Q_DS = [
    {'text':'Which Python library is used for numerical computing?','a':'Django','b':'NumPy','c':'Flask','d':'Requests','correct':'b'},
    {'text':'What does ETL stand for?','a':'Extract, Transform, Load','b':'Evaluate, Test, Learn','c':'Execute, Transfer, Log','d':'Extract, Test, Load','correct':'a'},
    {'text':'Pandas is primarily used for:','a':'Web development','b':'Data manipulation and analysis','c':'Machine learning only','d':'Plotting graphs','correct':'b'},
    {'text':'A scatter plot is best for showing:','a':'Distribution of a single variable','b':'Relationship between two variables','c':'Comparison of categories','d':'Change over time','correct':'b'},
    {'text':'What is the purpose of data cleaning?','a':'Deleting all data','b':'Handling missing values and correcting errors','c':'Creating visualisations','d':'Building models','correct':'b'},
    {'text':'SQL stands for:','a':'Structured Query Language','b':'Simple Query Language','c':'Standard Query Logic','d':'Sequential Query Language','correct':'a'},
    {'text':'Which of these is a supervised learning algorithm?','a':'K-means clustering','b':'Linear regression','c':'PCA','d':'Apriori','correct':'b'},
    {'text':'A histogram is used to show:','a':'Trends over time','b':'Distribution of numerical data','c':'Correlation between variables','d':'Categorical comparisons','correct':'b'},
    {'text':'What is overfitting?','a':'Model performs equally on training and test data','b':'Model performs well on training data but poorly on new data','c':'Model is too simple','d':'Model trains too slowly','correct':'b'},
    {'text':'Jupyter Notebook is commonly used for:','a':'Production deployment','b':'Interactive data analysis and prototyping','c':'Database management','d':'Network configuration','correct':'b'},
]

def add_program(title, desc, year_sem_names, paths_by_sem, pool):
    prog = Program.objects.create(title=title, description=desc)
    sems = [Semester.objects.create(program=prog, year_number=i//2+1, semester_number=i%2+1, name=name) for i, name in enumerate(year_sem_names)]
    print(f'\n{title} (id={prog.id})')
    for sem, path_list in zip(sems, paths_by_sem):
        for title, desc, topics, proj, steps, diff in path_list:
            p = cp(title, desc, bm(topics, proj, steps, pool), semester=sem, difficulty=diff)
            print(f'  {p.title} (id={p.id})')

@transaction.atomic
def main():
    # === DIPLOMA IN IT ===
    add_program('Diploma in Information Technology',
        'A two-year practical diploma preparing students for IT support, networking, and system administration roles.',
        ['IT Fundamentals','Networking and Web','Systems and Security','Cloud and Capstone'],
        [
            [('IT Fundamentals','Core IT concepts: hardware, software, OS, and troubleshooting.',['Computer Hardware','Operating Systems','Software Applications','File Management','Basic Troubleshooting','Internet Basics'],'IT Support',['Hardware Identification','Software Installation','Troubleshooting Scenarios','Support Documentation'],DIR.BEGINNER),
             ('Introduction to Programming','Basics of programming with Python: logic, variables, loops, functions.',['Programming Logic','Variables and Data Types','Control Structures','Functions','Simple Data Structures','Debugging'],'Programming',['Problem Solving','Algorithm Design','Program Implementation','Testing'],DIR.BEGINNER),
             ('Computer Hardware and Support','Hardware assembly, maintenance, and customer support.',['Hardware Components','System Assembly','Peripheral Devices','Preventive Maintenance','Customer Service Skills','Support Tools'],'Hardware',['Component Identification','System Assembly Lab','Maintenance Schedule','Support Simulation'],DIR.BEGINNER)],
            [('Networking Fundamentals','Network types, topologies, protocols, IP addressing, and configuration.',['Network Types and Topologies','OSI and TCP/IP Models','IP Addressing and Subnetting','Routing and Switching','Wireless Networking','Network Troubleshooting'],'Networking',['Network Design','IP Addressing Scheme','Router Configuration','Troubleshooting Lab'],DIR.INTERMEDIATE),
             ('Web Development Essentials','HTML, CSS, JavaScript, and responsive design.',['HTML5 and Structure','CSS and Styling','JavaScript Basics','Responsive Design','Web Forms','Web Publishing'],'Web',['Wireframe Design','HTML/CSS Development','JavaScript Integration','Website Deployment'],DIR.BEGINNER),
             ('Database Fundamentals','Relational databases, SQL, design, and administration.',['Database Concepts','ER Modelling','SQL Queries','Joins and Subqueries','Database Design','Data Integrity'],'Database',['Requirements Analysis','Schema Design','SQL Implementation','Query Optimisation'],DIR.INTERMEDIATE)],
            [('System Administration','Windows/Linux admin, user accounts, permissions, and maintenance.',['OS Installation','User and Group Management','File Permissions','System Monitoring','Backup and Recovery','Automation Scripting'],'Admin',['OS Installation','User Management Lab','Backup Strategy','Automation Script'],DIR.INTERMEDIATE),
             ('Cybersecurity Essentials','Security principles, threats, authentication, and encryption.',['Security Principles','Common Threats','Authentication Methods','Encryption Basics','Network Security','Security Policies'],'Security',['Threat Assessment','Security Controls','Encryption Lab','Policy Document'],DIR.INTERMEDIATE),
             ('IT Project Management','Project planning, scheduling, resource management, and documentation.',['Project Life Cycle','Project Planning','Scheduling','Resource Management','Risk Management','Project Documentation'],'Project',['Project Charter','WBS','Schedule and Budget','Closure Report'],DIR.INTERMEDIATE)],
            [('Cloud Computing Fundamentals','Cloud models, virtualisation, platforms, storage, and migration.',['Cloud Concepts','IaaS and Virtualisation','PaaS and Cloud Platforms','Cloud Storage','Cloud Security','Cloud Migration Basics'],'Cloud',['Architecture Design','Service Selection','Cloud Deployment','Cost Analysis'],DIR.INTERMEDIATE),
             ('IT Support and Operations','ITSM, help desk, SLAs, and ITIL framework.',['IT Service Management','Help Desk Operations','SLA and KPIs','Incident Management','ITIL Framework','Service Improvement'],'Operations',['Service Catalogue','Incident Process','SLA Definition','Improvement Plan'],DIR.INTERMEDIATE),
             ('Capstone: IT Solutions','Integrative IT project solving a real-world technology problem.',['Project Scoping','Requirements Analysis','Solution Design','Implementation','Testing','Presentation'],'Capstone',['Project Proposal','Design Document','Implementation','Final Presentation'],DIR.ADVANCED)],
        ], Q_IT)

    # === DIPLOMA IN BUSINESS MANAGEMENT ===
    add_program('Diploma in Business Management',
        'A two-year practical diploma developing foundational business knowledge and management skills.',
        ['Business Foundations','Marketing and Finance','People and Operations','Strategy and Capstone'],
        [
            [('Business Fundamentals','Core business concepts: types, environment, functions, ethics.',['Types of Business','Business Environment','Economic Systems','Business Functions','Stakeholders','Business Ethics'],'Business',['Business Type Analysis','Environmental Scan','Functional Review','Ethical Decision Making'],DIR.BEGINNER),
             ('Principles of Management','Management functions: planning, organising, leading, controlling.',['Management Functions','Planning and Goal Setting','Organisational Design','Leadership Styles','Control Processes','Decision Making'],'Management',['Case Analysis','Organisational Chart','Leadership Assessment','Control Design'],DIR.BEGINNER),
             ('Business Communication','Effective business writing, presentations, and interpersonal skills.',['Business Writing','Report Writing','Presentation Skills','Meeting Management','Digital Communication','Cross-Cultural Communication'],'Communication',['Letter Writing','Report Preparation','Presentation Delivery','Meeting Simulation'],DIR.BEGINNER)],
            [('Financial Accounting','Accounting principles, financial statements, bookkeeping.',['Accounting Principles','The Accounting Cycle','Financial Statements','Bookkeeping','Cash Flow','Financial Analysis'],'Accounting',['Transaction Recording','Statement Prep','Cash Flow Analysis','Financial Ratios'],DIR.INTERMEDIATE),
             ('Marketing Principles','Marketing concepts, research, consumer behaviour, branding.',['Marketing Concepts','Market Research','Consumer Behaviour','Branding','Digital Marketing','Marketing Strategy'],'Marketing',['Research Plan','Consumer Analysis','Brand Strategy','Marketing Plan'],DIR.INTERMEDIATE),
             ('Organisational Behaviour','Individual/group behaviour, motivation, teams, culture.',['Individual Behaviour','Motivation Theories','Team Dynamics','Organisational Culture','Power and Politics','Change Management'],'Behaviour',['Assessment','Motivation Analysis','Team Effectiveness','Culture Diagnosis'],DIR.INTERMEDIATE)],
            [('Human Resource Management','HR planning, recruitment, training, performance, compensation.',['HR Planning','Recruitment and Selection','Training and Development','Performance Management','Compensation','Employee Relations'],'HR',['Workforce Planning','Recruitment Process','Training Programme','Performance System'],DIR.INTERMEDIATE),
             ('Operations Management','Process design, quality, supply chain, inventory management.',['Operations Strategy','Process Design','Quality Management','Supply Chain','Inventory Management','Lean Operations'],'Operations',['Process Mapping','Quality Tools','Supply Chain Analysis','Lean Implementation'],DIR.INTERMEDIATE),
             ('Business Law','Legal environment: contracts, consumer law, employment law.',['Legal System','Contract Law','Consumer Protection','Employment Law','Business Entities','Intellectual Property'],'Law',['Contract Analysis','Consumer Case','Employment Scenario','Entity Comparison'],DIR.INTERMEDIATE)],
            [('Entrepreneurship','Opportunity recognition, business planning, financing, venture growth.',['Entrepreneurial Mindset','Opportunity Recognition','Business Model Canvas','Business Planning','Financing Ventures','Growth Strategies'],'Entrepreneurship',['Idea Validation','Business Model Canvas','Financial Projections','Pitch Deck'],DIR.ADVANCED),
             ('Strategic Management','Strategy formulation, competitive analysis, implementation.',['Strategy Concepts','Environmental Analysis','Internal Analysis','Strategy Formulation','Strategy Implementation','Strategy Evaluation'],'Strategy',['External Analysis','Internal Audit','Strategy Selection','Implementation Plan'],DIR.ADVANCED),
             ('Capstone: Business Project','Comprehensive business plan and management strategy.',['Project Scoping','Market Analysis','Business Plan','Financial Planning','Implementation Plan','Presentation'],'Capstone',['Project Proposal','Market Research','Business Plan','Final Presentation'],DIR.ADVANCED)],
        ], Q_BUS)

    # === DIPLOMA IN SOFTWARE ENGINEERING ===
    add_program('Diploma in Software Engineering',
        'A two-year practical diploma equipping students with software development, testing, and project management skills.',
        ['Programming Fundamentals','OOP and Design','Development and Testing','Mobile and Capstone'],
        [
            [('Programming Fundamentals','Core programming with Python: data types, control flow, functions.',['Python Basics','Data Types and Variables','Control Flow','Functions','Data Structures','File Handling'],'Programming',['Problem Decomposition','Algorithm Design','Implementation','Testing'],DIR.BEGINNER),
             ('Web Development Basics','HTML, CSS, JavaScript, responsive design.',['HTML Structure','CSS Styling','JavaScript Fundamentals','DOM Manipulation','Responsive Design','Web Forms'],'Web',['Wireframe','HTML/CSS Build','JavaScript Features','Responsive Site'],DIR.BEGINNER),
             ('Database Design and SQL','Relational databases, SQL, normalisation.',['Database Concepts','ER Diagrams','SQL DDL and DML','Joins and Aggregations','Normalisation','Database Connectivity'],'Database',['ER Design','Schema Creation','Query Development','App Integration'],DIR.BEGINNER)],
            [('Object-Oriented Programming','OOP principles with Java: classes, inheritance, polymorphism.',['Classes and Objects','Inheritance','Polymorphism','Interfaces','Exception Handling','Collections Framework'],'OOP',['Class Design','Inheritance Hierarchy','Polymorphism Demo','Collection App'],DIR.INTERMEDIATE),
             ('Data Structures','Arrays, linked lists, stacks, queues, trees, hash tables.',['Arrays and Lists','Linked Lists','Stacks and Queues','Trees','Hash Tables','Algorithm Complexity'],'Data',['Structure Selection','Implementation','Performance Testing','Complexity Analysis'],DIR.INTERMEDIATE),
             ('UI/UX Design Principles','User-centred design, wireframing, prototyping, usability.',['User-Centred Design','Wireframing','Prototyping','Visual Design','Usability Testing','Accessibility'],'UI',['User Research','Wireframe and Prototype','Usability Test','Design Portfolio'],DIR.INTERMEDIATE)],
            [('Software Design and Architecture','Architecture patterns, UML, system design, APIs.',['Architecture Patterns','SOLID Principles','UML Modelling','System Design','API Design','Documentation'],'Architecture',['System Requirements','UML Diagrams','Architecture Document','API Spec'],DIR.INTERMEDIATE),
             ('Software Testing and QA','Testing types, planning, automation, quality assurance.',['Testing Fundamentals','Test Planning','Manual Testing','Test Automation','Performance Testing','QA Processes'],'Testing',['Test Plan','Manual Test Cases','Automation Scripts','QA Report'],DIR.INTERMEDIATE),
             ('Agile and DevOps Methodologies','Agile, Scrum, Kanban, CI/CD, DevOps practices.',['Agile Principles','Scrum Framework','Sprint Management','Kanban','CI/CD Pipelines','DevOps Culture'],'Agile',['Product Backlog','Sprint Simulation','CI/CD Pipeline','Retrospective'],DIR.INTERMEDIATE)],
            [('Mobile App Development','React Native: components, navigation, state, deployment.',['Mobile Development Overview','React Native Basics','Components and Navigation','State Management','API Integration','App Deployment'],'Mobile',['App Design','Component Development','Feature Implementation','Deployment'],DIR.ADVANCED),
             ('DevOps and Deployment','Docker, Kubernetes, cloud deployment, monitoring.',['Docker Fundamentals','Docker Compose','Kubernetes Basics','Cloud Deployment','Monitoring and Logging','IaC'],'DevOps',['Containerisation','Orchestration Setup','Pipeline Setup','Monitoring Dashboard'],DIR.ADVANCED),
             ('Capstone: Software Project','Full SDLC project: requirements to deployment.',['Project Planning','Requirements','Design and Architecture','Sprint Implementation','Testing','Deployment'],'Capstone',['Project Charter','Design Document','Working Application','Final Presentation'],DIR.ADVANCED)],
        ], Q_SE)

    # === DIPLOMA IN DATA SCIENCE ===
    add_program('Diploma in Data Science',
        'A one-year intensive diploma providing practical data science skills for entry-level data analyst roles.',
        ['Data Foundations','Applied Analytics'],
        [
            [('Python for Data Science','NumPy, Pandas, data cleaning, exploratory analysis.',['Python Refresher','NumPy for Numerical Data','Pandas DataFrames','Data Cleaning','Data Transformation','Exploratory Analysis'],'Data',['Data Loading','Data Cleaning Pipeline','Exploratory Analysis','Summary Report'],DIR.BEGINNER),
             ('Statistics Essentials','Descriptive and inferential statistics, hypothesis testing.',['Descriptive Statistics','Probability','Distributions','Sampling','Hypothesis Testing','Correlation'],'Statistics',['Descriptive Analysis','Probability Calculations','Hypothesis Test','Correlation Study'],DIR.BEGINNER),
             ('Data Wrangling and SQL','ETL, SQL, web scraping, API data collection.',['Data Sources and Formats','SQL for Analysts','Joins and Subqueries','Data Transformation','Web Scraping','API Data Collection'],'Wrangling',['Data Source Integration','SQL Queries','Data Transformation','Pipeline Creation'],DIR.INTERMEDIATE)],
            [('Machine Learning Basics','Regression, classification, clustering, model evaluation.',['ML Fundamentals','Linear Regression','Classification','Decision Trees','Clustering','Model Evaluation'],'Machine Learning',['Problem Definition','Model Training','Evaluation','Model Comparison'],DIR.INTERMEDIATE),
             ('Data Visualisation','Matplotlib, Seaborn, Tableau, dashboards.',['Visualisation Principles','Matplotlib','Seaborn','Tableau Basics','Dashboard Design','Data Storytelling'],'Data Visualisation',['Chart Selection','Statistical Plots','Interactive Dashboard','Presentation'],DIR.INTERMEDIATE),
             ('Capstone: Data Analytics','End-to-end analytics project: collection to insights.',['Project Scoping','Data Collection','Data Cleaning and Analysis','Modelling','Visualisation','Presentation'],'Data Capstone',['Project Plan','Analysis Notebook','Dashboard','Final Presentation'],DIR.ADVANCED)],
        ], Q_DS)

    print(f'\n=== GLOBAL SUMMARY ===')
    print(f'Programs: {Program.objects.count()}')
    print(f'Semesters: {Semester.objects.count()}')
    print(f'LearningPaths: {LearningPath.objects.count()}')
    print(f'Modules: {Module.objects.count()}')
    print(f'Lessons: {Lesson.objects.count()}')

if __name__ == '__main__':
    main()
