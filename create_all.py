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
    total_min += sum(len(md['lessons']) * md.get('duration', 10) for md in modules_data)
    path.estimated_hours = round(total_min / 60)
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

Q_ACCA = [
    {'text':'Under IFRS 15, revenue is recognised when:','a':'Cash is received','b':'Control of goods/services passes to customer','c':'Invoice is issued','d':'Contract is signed','correct':'b'},
    {'text':'What does the accruals concept require?','a':'Revenue recorded when cash received','b':'Expenses matched to period incurred, not paid','c':'Assets recorded at market value','d':'Liabilities ignored until paid','correct':'b'},
    {'text':'Which ratio measures short-term liquidity?','a':'Return on capital employed','b':'Current ratio','c':'Debt-to-equity','d':'Gross profit margin','correct':'b'},
    {'text':'An external audit provides:','a':'Absolute assurance','b':'Reasonable assurance','c':'Limited assurance','d':'No assurance','correct':'b'},
    {'text':'The IASB is responsible for:','a':'Setting tax rates','b':'Developing IFRS standards','c':'Regulating stock markets','d':'Auditing companies','correct':'b'},
    {'text':'What is a materiality threshold?','a':'Maximum allowed tax deduction','b':'Amount that influences user decisions','c':'Minimum share capital','d':'Maximum dividend payment','correct':'b'},
    {'text':'Variance analysis compares:','a':'Actual vs budgeted performance','b':'Current vs prior year','c':'Competitor performance','d':'Industry averages','correct':'a'},
    {'text':'Which is a fixed cost?','a':'Raw materials','b':'Factory rent','c':'Direct labour','d':'Sales commission','correct':'b'},
    {'text':'A rights issue involves:','a':'Issuing shares to the public','b':'Offering shares to existing shareholders','c':'Buying back shares','d':'Paying dividends in shares','correct':'b'},
    {'text':'IAS 36 covers:','a':'Revenue recognition','b':'Impairment of assets','c':'Inventory valuation','d':'Lease accounting','correct':'b'},
]

Q_CPA = [
    {'text':'Under ASC 606, revenue is recognised:','a':'When cash is collected','b':'When performance obligations are satisfied','c':'At contract signing','d':'At year-end','correct':'b'},
    {'text':'What is audit risk?','a':'Risk of business failure','b':'Risk auditor issues incorrect opinion','c':'Risk of fraud','d':'Risk of non-compliance','correct':'b'},
    {'text':'Which standard governs lease accounting under US GAAP?','a':'ASC 606','b':'ASC 842','c':'ASC 718','d':'ASC 740','correct':'b'},
    {'text':'The effective interest method applies to:','a':'Inventory valuation','b':'Bond premium/discount amortisation','c':'Depreciation','d':'Tax calculation','correct':'b'},
    {'text':'SOX Section 404 requires:','a':'External audit only','b':'Management assessment of internal controls','c':'Quarterly earnings forecasts','d':'Board diversity disclosures','correct':'b'},
    {'text':'A Type I subsequent event:','a':'Occurs after year-end with no adjustment needed','b':'Provides evidence of conditions at year-end','c':'Requires pro-forma disclosure only','d':'Is always disclosed in footnotes','correct':'b'},
    {'text':'Under US GAAP, development costs are:','a':'Always capitalised','b':'Generally expensed as incurred','c':'Capitalised only for software','d':'Amortised over 20 years','correct':'b'},
    {'text':'PCAOB inspections apply to:','a':'All public companies','b':'Registered public accounting firms','c':'Private company auditors only','d':'Government auditors','correct':'b'},
    {'text':'What is a contingent liability?','a':'Liability with fixed payment date','b':'Potential liability depending on future events','c':'Liability settled within 12 months','d':'Liability with zero interest','correct':'b'},
    {'text':'The COSO framework relates to:','a':'Financial reporting','b':'Internal control','c':'Tax compliance','d':'Corporate governance','correct':'b'},
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
    # === BSc Information Technology ===
    add_program('BSc Information Technology',
        'A comprehensive four-year degree programme covering programming, networking, databases, web, AI, security, and professional practice.',
        ['Year 1 Semester 1','Year 1 Semester 2','Year 2 Semester 1','Year 2 Semester 2','Year 3 Semester 1','Year 3 Semester 2','Year 4 Semester 1','Year 4 Semester 2'],
        [
            [('Introduction to Programming','Fundamentals of programming using Python.',['Programming Concepts','Variables and Data Types','Control Structures','Functions','Lists and Dictionaries','File I/O'],'Programming',['Problem Decomposition','Algorithm Design','Program Implementation','Testing and Debugging'],DIR.BEGINNER),
             ('Computer Systems Fundamentals','Hardware, software, number systems, operating systems.',['Digital Logic','Computer Architecture','Operating Systems','Memory Management','Storage Systems','Peripheral Devices'],'Computer Systems',['Hardware Identification','OS Installation','System Configuration','Performance Monitoring'],DIR.BEGINNER),
             ('Mathematics for Computing','Set theory, logic, matrices, combinatorics, probability.',['Set Theory','Propositional Logic','Matrices','Combinatorics','Probability','Graph Theory'],'Mathematics',['Set Operations','Logic Proofs','Matrix Calculations','Probability Problems'],DIR.BEGINNER),
             ('Communication and Academic Skills','Academic writing, research, presentation skills.',['Academic Writing','Research Methods','Critical Thinking','Presentation Skills','Referencing','Group Work'],'Academic Skills',['Research Proposal','Academic Essay','Presentation','Peer Review'],DIR.BEGINNER),
             ('Web Development Fundamentals','HTML, CSS, JavaScript, responsive design.',['HTML5','CSS3','JavaScript','DOM Manipulation','Responsive Design','Web Publishing'],'Web Development',['Wireframe','HTML/CSS Build','Interactive Features','Responsive Site'],DIR.BEGINNER),
             ('Database Systems','Relational databases, SQL, normalisation, ER modelling.',['Database Concepts','ER Modelling','SQL DDL','SQL DML','Normalisation','Transactions'],'Database',['ER Design','Schema Creation','Query Implementation','Normalisation Exercise'],DIR.BEGINNER),
             ('Networking Essentials','Network types, OSI model, TCP/IP, IP addressing.',['Network Types','OSI Model','TCP/IP Suite','IP Addressing','Routing','Network Security Basics'],'Networking',['Network Design','IP Addressing Scheme','Cable and Configure','Packet Analysis'],DIR.BEGINNER),
             ('Operating Systems','Process management, memory, file systems, security.',['Process Management','CPU Scheduling','Memory Management','File Systems','I/O Management','OS Security'],'Operating Systems',['Process Simulation','Scheduling Algorithms','Memory Allocation','File System Lab'],DIR.INTERMEDIATE),
             ('Software Engineering Fundamentals','SDLC, requirements, design, testing, project management.',['SDLC Models','Requirements Engineering','System Design','Implementation','Testing Strategies','Project Management'],'Software Engineering',['Requirements Document','System Design','Implementation Plan','Test Plan'],DIR.INTERMEDIATE)],
            [('Object-Oriented Programming','OOP with Java: classes, inheritance, polymorphism.',['Classes and Objects','Inheritance','Polymorphism','Interfaces','Exception Handling','Generics'],'OOP',['Class Design','Inheritance Hierarchy','Polymorphism Demo','Exception Handling'],DIR.INTERMEDIATE),
             ('Data Structures and Algorithms','Arrays, linked lists, trees, graphs, sorting, searching.',['Arrays and Lists','Stacks and Queues','Trees and Graphs','Hash Tables','Sorting Algorithms','Searching Algorithms'],'Data Structures',['Data Structure Selection','Implementation','Complexity Analysis','Algorithm Comparison'],DIR.INTERMEDIATE),
             ('Discrete Mathematics','Logic, proof techniques, counting, relations, graphs.',['Mathematical Logic','Proof Techniques','Counting Principles','Relations and Functions','Graph Theory','Boolean Algebra'],'Discrete Mathematics',['Logic Proofs','Counting Problems','Graph Analysis','Boolean Simplification'],DIR.INTERMEDIATE),
             ('Human-Computer Interaction','Usability, design principles, prototyping, evaluation.',['HCI Fundamentals','User Research','Design Principles','Prototyping','Usability Evaluation','Accessibility'],'HCI',['User Research','Wireframe and Prototype','Usability Test','Design Portfolio'],DIR.INTERMEDIATE),
             ('Data Communication','Transmission media, multiplexing, error detection.',['Transmission Media','Multiplexing','Error Detection','Flow Control','Protocols','Network Performance'],'Data Communication',['Media Comparison','Multiplexing Demo','Error Detection Lab','Performance Analysis'],DIR.INTERMEDIATE),
             ('Systems Analysis and Design','Structured and object-oriented analysis, UML.',['System Analysis','UML Modelling','Structured Design','Object-Oriented Design','Design Patterns','System Documentation'],'Systems Analysis',['Requirements Analysis','Use Case Diagrams','Class Diagrams','Design Specification'],DIR.INTERMEDIATE),
             ('Ethics and Professional Practice','Professional ethics, intellectual property, privacy.',['Professional Ethics','Intellectual Property','Privacy and Data Protection','Cybercrime','Professional Standards','Social Impact'],'Ethics',['Ethical Analysis','Case Study','Policy Proposal','Code of Conduct'],DIR.INTERMEDIATE),
             ('Probability and Statistics','Probability, distributions, sampling, hypothesis testing.',['Probability Fundamentals','Random Variables','Distributions','Sampling','Hypothesis Testing','Regression'],'Statistics',['Probability Problems','Distribution Analysis','Hypothesis Test','Regression Analysis'],DIR.INTERMEDIATE)],
            [('Advanced Programming','Advanced Java: concurrency, networking, GUI, databases.',['Concurrency','Network Programming','GUI Development','Database Connectivity','Design Patterns','Reflection'],'Advanced Programming',['Thread Implementation','Socket Programming','GUI Application','Database Integration'],DIR.ADVANCED),
             ('Algorithm Design and Analysis','Design paradigms, complexity, NP-completeness.',['Algorithm Paradigms','Divide and Conquer','Dynamic Programming','Greedy Algorithms','Complexity Classes','NP-Completeness'],'Algorithms',['Paradigm Selection','Algorithm Implementation','Complexity Analysis','NP Problem Identification'],DIR.ADVANCED),
             ('Computer Networks','Network architectures, protocols, routing, security.',['Network Architecture','Routing Protocols','Transport Layer','Application Layer','Network Security','Network Management'],'Networks',['Network Design','Routing Configuration','Protocol Analysis','Security Assessment'],DIR.ADVANCED),
             ('Database Administration','Advanced SQL, indexing, query optimisation, security.',['Advanced SQL','Indexing and Performance','Query Optimisation','Database Security','Backup and Recovery','Distributed Databases'],'Database Admin',['Performance Tuning','Security Implementation','Backup Strategy','Distributed Design'],DIR.ADVANCED),
             ('Web Application Development','Full-stack: React, Node.js, REST, deployment.',['Frontend Frameworks','Backend Development','REST API Design','Authentication','State Management','Deployment'],'Web Application',['Frontend Implementation','API Development','Auth Integration','Deployment Pipeline'],DIR.ADVANCED),
             ('Information Systems','IS types, ERP, CRM, business intelligence.',['Information Systems Overview','Transaction Processing','ERP Systems','CRM Systems','Business Intelligence','IS Strategy'],'Information Systems',['IS Needs Analysis','ERP Module Design','BI Dashboard','IS Strategy Plan'],DIR.ADVANCED),
             ('Research Methods','Research design, data collection, statistical analysis.',['Research Design','Literature Review','Data Collection Methods','Statistical Analysis','Qualitative Analysis','Research Ethics'],'Research',['Research Proposal','Literature Review','Data Analysis','Research Report'],DIR.ADVANCED),
             ('Mobile Application Development','Android/iOS development with React Native.',['Mobile Platform Overview','React Native Basics','Navigation and State','Device Features','App Testing','App Deployment'],'Mobile Development',['App Design','Feature Development','Testing','Deployment'],DIR.ADVANCED)],
            [('Artificial Intelligence','Search, knowledge representation, machine learning.',['AI Fundamentals','Search Algorithms','Knowledge Representation','Machine Learning','Neural Networks','AI Ethics'],'AI',['Search Implementation','Knowledge Base','ML Model','Ethical Analysis'],DIR.ADVANCED),
             ('Compiler Design','Lexical analysis, parsing, code generation.',['Language Processors','Lexical Analysis','Syntax Analysis','Semantic Analysis','Code Generation','Optimisation'],'Compiler',['Lexer Implementation','Parser Construction','Code Generation','Optimisation'],DIR.ADVANCED),
             ('Network Security','Cryptography, secure protocols, firewalls, IDS.',['Cryptography','Secure Protocols','Firewalls','Intrusion Detection','VPNs','Security Policies'],'Network Security',['Encryption Lab','Firewall Configuration','IDS Setup','Security Policy'],DIR.ADVANCED),
             ('Enterprise Application Development','J2EE/Spring, microservices, cloud deployment.',['Enterprise Architecture','Spring Framework','Microservices','RESTful Services','Cloud Deployment','Monitoring'],'Enterprise',['Spring Boot Application','Microservices Design','Cloud Deployment','Monitoring Setup'],DIR.ADVANCED),
             ('Data Mining and Warehousing','Data warehouse design, OLAP, association, clustering.',['Data Warehousing','ETL Processes','OLAP','Association Rules','Clustering','Text Mining'],'Data Mining',['Warehouse Design','ETL Pipeline','Association Mining','Clustering Analysis'],DIR.ADVANCED),
             ('Human Resource Management','HR functions, recruitment, performance management.',['HR Planning','Recruitment','Training','Performance Management','Compensation','Employee Relations'],'HR',['Workforce Plan','Recruitment Process','Training Programme','Performance System'],DIR.INTERMEDIATE),
             ('Distributed Systems','Distributed architectures, consistency, replication.',['Distributed Architectures','Communication','Consistency','Replication','Fault Tolerance','Distributed File Systems'],'Distributed Systems',['Architecture Design','Communication Protocol','Consistency Model','Fault Tolerance Lab'],DIR.ADVANCED),
             ('Computer Graphics','Graphics pipeline, transformations, rendering.',['Graphics Pipeline','Transformations','Colour Models','Rendering','Animation','Graphics APIs'],'Graphics',['Scene Modelling','Transformations','Rendering Pipeline','Animation'],DIR.ADVANCED)],
            [('Machine Learning','Regression, classification, neural networks, SVM.',['ML Fundamentals','Linear Regression','Classification','Neural Networks','Support Vector Machines','Ensemble Methods'],'ML',['Data Preparation','Model Training','Evaluation','Hyperparameter Tuning'],DIR.ADVANCED),
             ('Software Project Management','Project planning, estimation, risk, agile.',['Project Planning','Estimation','Risk Management','Agile Methodologies','Project Monitoring','Quality Management'],'Software PM',['Project Plan','Estimation','Risk Assessment','Sprint Simulation'],DIR.ADVANCED),
             ('Cloud Computing','IaaS, PaaS, SaaS, virtualisation, containers.',['Cloud Models','Virtualisation','Containers','Cloud Storage','Serverless','Cloud Security'],'Cloud Computing',['Architecture Design','Container Setup','Serverless Function','Security Assessment'],DIR.ADVANCED),
             ('Big Data Analytics','Hadoop, Spark, MapReduce, stream processing.',['Big Data Overview','Hadoop Ecosystem','MapReduce','Apache Spark','Stream Processing','NoSQL Databases'],'Big Data',['Hadoop Setup','MapReduce Job','Spark Analysis','Stream Processing'],DIR.ADVANCED),
             ('Internet of Things','IoT architecture, sensors, protocols, platforms.',['IoT Overview','Architecture','Sensors and Actuators','IoT Protocols','IoT Platforms','IoT Security'],'IoT',['Architecture Design','Sensor Integration','Protocol Implementation','Security Plan'],DIR.ADVANCED),
             ('Financial Management','Financial analysis, budgeting, investment decisions.',['Financial Analysis','Budgeting','Investment Appraisal','Cost Management','Financial Reporting','Working Capital'],'Financial Management',['Financial Analysis','Budget Preparation','Investment Appraisal','Working Capital Plan'],DIR.INTERMEDIATE),
             ('Data Visualisation','Data storytelling, dashboards, Tableau, D3.js.',['Visualisation Principles','Chart Types','Dashboard Design','Tableau','D3.js','Data Storytelling'],'Data Visualisation',['Chart Selection','Dashboard Creation','Interactive Visualisation','Presentation'],DIR.ADVANCED),
             ('Capstone Project I','Proposal, literature review, system design.',['Project Scoping','Literature Review','Requirements','System Design','Methodology','Project Plan'],'Capstone I',['Project Proposal','Literature Review','Design Document','Project Plan'],DIR.ADVANCED)],
            [('Cyber Security','Security architecture, risk management, forensics.',['Security Architecture','Risk Management','Digital Forensics','Incident Response','Penetration Testing','Compliance'],'Cyber Security',['Risk Assessment','Forensic Analysis','Pen Test Lab','Incident Response Plan'],DIR.ADVANCED),
             ('Computer Vision','Image processing, feature detection, CNNs.',['Image Processing','Feature Detection','Object Recognition','CNNs','Video Analysis','Vision Applications'],'Computer Vision',['Image Processing','Feature Detection','CNN Implementation','Application Development'],DIR.ADVANCED),
             ('Natural Language Processing','Text processing, embeddings, transformers.',['Text Processing','Language Modelling','Word Embeddings','RNNs and LSTMs','Transformers','NLP Applications'],'NLP',['Text Processing Pipeline','Language Model','Transformer Implementation','NLP Application'],DIR.ADVANCED),
             ('DevOps and Continuous Delivery','CI/CD, Docker, Kubernetes, IaC.',['DevOps Culture','CI/CD Pipelines','Docker','Kubernetes','Infrastructure as Code','Monitoring'],'DevOps',['CI/CD Setup','Containerisation','K8s Deployment','IaC Implementation'],DIR.ADVANCED),
             ('Blockchain Technology','Distributed ledgers, smart contracts, DApps.',['Blockchain Fundamentals','Distributed Ledgers','Smart Contracts','Ethereum','DApp Development','Blockchain Use Cases'],'Blockchain',['Blockchain Design','Smart Contract Dev','DApp Development','Use Case Analysis'],DIR.ADVANCED),
             ('Entrepreneurship','Business models, funding, growth strategies.',['Entrepreneurial Mindset','Business Models','Funding','Growth Strategies','Innovation Management','Exit Strategies'],'Entrepreneurship',['Business Model Canvas','Financial Projections','Pitch Deck','Growth Plan'],DIR.INTERMEDIATE),
             ('Information Security Management','ISMS, standards, risk treatment.',['ISMS','ISO 27001','Risk Treatment','Security Controls','BCP and DRP','Audit and Compliance'],'InfoSec',['ISMS Scope','Risk Treatment Plan','BCP Development','Audit Checklist'],DIR.ADVANCED),
             ('Capstone Project II','Implementation, testing, deployment, defence.',['Implementation','Testing','Deployment','Documentation','User Training','Project Defence'],'Capstone II',['Implementation','Test Report','Deployment Guide','Final Defence'],DIR.ADVANCED)],
            [('Deep Learning','CNNs, RNNs, GANs, transformers, transfer learning.',['Deep Learning Fundamentals','CNNs','RNNs and LSTMs','GANs','Transformers','Transfer Learning'],'Deep Learning',['CNN Implementation','RNN Implementation','GAN Training','Transfer Learning'],DIR.ADVANCED),
             ('Software Quality Assurance','Quality models, metrics, reviews, automation.',['Quality Models','Quality Metrics','Code Reviews','Static Analysis','Test Automation','Continuous Quality'],'SQA',['Quality Plan','Metric Definition','Test Automation','Quality Report'],DIR.ADVANCED),
             ('Advanced Database Systems','NoSQL, NewSQL, distributed databases.',['NoSQL Types','Document Stores','Key-Value Stores','Graph Databases','NewSQL','Distributed DBMS'],'Advanced DB',['DB Selection','Document Store Setup','Graph Query','Performance Benchmark'],DIR.ADVANCED),
             ('IT Governance and Strategy','COBIT, ITIL, strategic alignment, value delivery.',['IT Governance Frameworks','COBIT','ITIL','Strategic Alignment','Value Delivery','Performance Measurement'],'IT Governance',['Governance Framework','ITIL Process','Strategic Plan','Performance Dashboard'],DIR.ADVANCED),
             ('Advanced Web Technologies','WebSockets, PWAs, JAMstack, serverless.',['WebSockets','Progressive Web Apps','JAMstack','Serverless Web','Edge Computing','Web Performance'],'Advanced Web',['WebSocket App','PWA Implementation','JAMstack Site','Performance Optimisation'],DIR.ADVANCED),
             ('Professional Development','Career planning, CV writing, interview skills.',['Career Planning','CV and Portfolio','Interview Skills','Networking','Professional Ethics Review','Lifelong Learning'],'Professional Development',['Career Plan','CV and Portfolio','Mock Interview','Professional Development Plan'],DIR.INTERMEDIATE),
             ('E-Commerce and Digital Business','E-commerce models, platforms, security, analytics.',['E-Commerce Models','Platforms','Payment Systems','Security','Digital Marketing','Analytics'],'E-Commerce',['Business Model','Platform Selection','Security Plan','Marketing Strategy'],DIR.ADVANCED),
             ('Capstone Project III',('Advanced implementation, integration, optimisation, final report.'),['Advanced Implementation','System Integration','Optimisation','Final Report','Presentation','Demonstration'],'Capstone III',['Advanced Implementation','Integration Report','Optimisation Results','Final Report'],DIR.ADVANCED)],
            [('Quantum Computing','Qubits, quantum gates, algorithms, applications.',['Quantum Basics','Qubits','Quantum Gates','Quantum Algorithms','Quantum Applications','Future of QC'],'Quantum Computing',['Qubit Simulation','Gate Implementation','Algorithm Demo','Application Analysis'],DIR.ADVANCED),
             ('Edge Computing','Edge architecture, fog computing, use cases.',['Edge Computing Overview','Architecture','Fog Computing','Edge AI','Edge Security','Use Cases'],'Edge Computing',['Architecture Design','Edge AI Implementation','Security Plan','Use Case Analysis'],DIR.ADVANCED),
             ('Advanced AI','Reinforcement learning, explainable AI, ethics.',['Reinforcement Learning','Explainable AI','AI Safety','Advanced NLP','Multi-Agent Systems','AI Ethics'],'Advanced AI',['RL Implementation','Explainability Demo','Safety Analysis','Ethical Framework'],DIR.ADVANCED),
             ('Digital Transformation','Strategy, change management, emerging tech.',['Digital Strategy','Change Management','Emerging Technologies','Digital Maturity','Innovation Labs','Transformation Roadmap'],'Digital Transformation',['Strategy Document','Change Plan','Technology Assessment','Transformation Roadmap'],DIR.ADVANCED),
             ('Cybersecurity Operations','SOC, threat hunting, incident response.',['Security Operations Centre','Threat Intelligence','Threat Hunting','Incident Response','Forensics','Security Automation'],'Cyber Ops',['SOC Design','Threat Hunt Exercise','Incident Response Plan','Automation Script'],DIR.ADVANCED),
             ('Industry Attachment','Practical industry experience and report.',['Workplace Orientation','Project Assignment','Progress Review','Final Report','Presentation','Evaluation'],'Industry Attachment',['Work Plan','Progress Report','Final Report','Presentation'],DIR.ADVANCED),
             ('Final Year Project','Comprehensive research and development project.',['Project Definition','Literature Review','Design and Methodology','Implementation','Testing and Evaluation','Defence'],'Final Year Project',['Project Proposal','Literature Review','Design Document','Final Report'],DIR.ADVANCED)],
        ], Q_IT)

    # === ACCA Qualification ===
    add_program('ACCA Qualification',
        'Association of Chartered Certified Accountants - Professional Accountancy Qualification',
        ['Applied Knowledge','Applied Skills','Strategic Professional - Essentials','Strategic Professional - Options'],
        [
            [('Accountant in Business','Business organisation, governance, ethics, management.',['Business Organisation','Stakeholders','Corporate Governance','Ethics','Management','Leadership'],'Business',['Organisation Analysis','Stakeholder Map','Ethical Decision','Management Assessment'],DIR.BEGINNER),
             ('Management Accounting','Costing, budgeting, performance measurement.',['Cost Classification','Costing Methods','Budgeting','Standard Costing','Variance Analysis','Performance Measurement'],'Management Accounting',['Cost Analysis','Budget Preparation','Variance Calculation','Performance Report'],DIR.BEGINNER),
             ('Financial Accounting','Financial records, statements, reporting.',['Accounting Principles','Double Entry','Trial Balance','Financial Statements','Control Accounts','Bank Reconciliation'],'Financial Accounting',['Journal Entries','Statement Preparation','Control Account','Bank Reconciliation'],DIR.BEGINNER)],
            [('Corporate and Business Law','Legal system, contract, tort, employment law.',['Legal System','Contract Law','Tort Law','Employment Law','Company Law','Insolvency'],'Law',['Contract Analysis','Tort Case Study','Company Formation','Insolvency Scenario'],DIR.INTERMEDIATE),
             ('Performance Management','Advanced costing, decision making, budgeting.',['Advanced Costing','Decision Making','Budgetary Control','Transfer Pricing','Performance Management','Divisional Performance'],'Performance Management',['Costing Analysis','Decision Analysis','Budget Review','Performance Report'],DIR.INTERMEDIATE),
             ('Taxation','Tax system, income tax, VAT, inheritance tax.',['Tax System','Income Tax','Corporation Tax','VAT','Capital Gains','Inheritance Tax'],'Taxation',['Tax Calculation','Corporation Tax','VAT Return','Tax Planning'],DIR.INTERMEDIATE),
             ('Financial Reporting','IFRS, financial statements, consolidation.',['IFRS Framework','Financial Statements','Consolidation','Revenue Recognition','Leases','Financial Instruments'],'Financial Reporting',['Statement Preparation','Consolidation','Revenue Analysis','Disclosure Checklist'],DIR.INTERMEDIATE),
             ('Audit and Assurance','Audit process, evidence, review, reporting.',['Audit Framework','Planning','Audit Evidence','Internal Control','Audit Review','Reporting'],'Audit',['Audit Plan','Control Testing','Substantive Testing','Audit Report'],DIR.INTERMEDIATE),
             ('Financial Management','Investment, financing, dividend decisions.',['Financial Management Role','Investment Appraisal','Cost of Capital','Financing','Dividend Policy','Risk Management'],'Financial Management',['Investment Appraisal','Capital Structure','Dividend Decision','Risk Assessment'],DIR.INTERMEDIATE)],
            [('Strategic Business Leader','Strategic leadership, governance, risk, technology.',['Strategic Leadership','Corporate Governance','Risk Management','Technology and Data','Strategic Analysis','Organisational Control'],'SBL',['Strategic Analysis','Governance Review','Risk Assessment','Digital Strategy'],DIR.ADVANCED),
             ('Strategic Business Reporting','Advanced financial reporting, group accounts, ethics.',['Professional Appointments','Ethical Requirements','Group Accounting','Share-Based Payments','Financial Instruments','Integrated Reporting'],'SBR',['Business Report','Consolidation','Disclosures','Integrated Report'],DIR.ADVANCED)],
            [('Advanced Financial Management','Advanced investment, treasury, M&A.',['Advanced Investment','Treasury Management','Mergers and Acquisitions','Business Valuation','Risk Management','International Finance'],'AFM',['Investment Analysis','Treasury Policy','Valuation','M&A Evaluation'],DIR.ADVANCED),
             ('Advanced Audit and Assurance','Advanced audit, current issues, professional liability.',['Regulatory Environment','Advanced Audit','Current Issues','Professional Liability','Quality Control','Audit Automation'],'AAA',['Audit Strategy','Advanced Procedures','Current Issue Analysis','Quality Control'],DIR.ADVANCED),
             ('Advanced Taxation','Advanced tax planning, ethics, HMRC powers.',['Tax Compliance','Tax Planning','Corporation Tax','International Tax','HMRC Powers','Professional Ethics'],'ATX',['Tax Compliance','International Tax','Ethical Scenario','Tax Planning'],DIR.ADVANCED)],
        ], Q_ACCA)

    # === CPA Certification ===
    add_program('CPA Certification',
        'Certified Public Accountant - US CPA licensure preparation covering all core and discipline sections of the CPA Evolution exam',
        ['Core Sections','Discipline Sections'],
        [
            [('FAR - Financial Accounting and Reporting','US GAAP, financial statements, ASC topics.',['ASC Framework','Financial Statements','Revenue Recognition','Leases','Pensions','Equity'],'FAR',['Statement Preparation','Revenue Analysis','Lease Accounting','Comprehensive Problem'],DIR.ADVANCED),
             ('AUD - Auditing and Attestation','Audit process, evidence, reporting, AICPA standards.',['Audit Standards','Planning','Risk Assessment','Evidence','Reporting','AICPA Standards'],'AUD',['Audit Plan','Risk Assessment','Evidence Procedures','Audit Report'],DIR.ADVANCED),
             ('REG - Regulation','Taxation, business law, ethics, professional responsibilities.',['Federal Taxation','Property Transactions','Business Law','Ethics','Professional Responsibilities','Regulatory Framework'],'REG',['Tax Return Preparation','Property Transaction','Business Analysis','Ethical Case'],DIR.ADVANCED)],
            [('BAR - Business Analysis and Reporting','Financial analysis, reporting, valuation.',['Financial Analysis','Business Reporting','Valuation','Forecasting','Segment Reporting','MD&A Analysis'],'BAR',['Financial Analysis','Business Report','Valuation Model','Forecasting'],DIR.ADVANCED),
             ('ISC - Information Systems and Controls','IT audit, cybersecurity, data management.',['IT Governance','Cybersecurity','Data Management','System Controls','IT Audit','Business Continuity'],'ISC',['Control Assessment','Security Review','Data Governance','IT Audit Report'],DIR.ADVANCED),
             ('TCP - Taxation and Compliance','Advanced tax compliance, estate tax, exempt organisations.',['Tax Compliance','Estate Tax','Gift Tax','Exempt Organisations','Multistate Tax','Tax Research'],'TCP',['Compliance Return','Estate Planning','Exempt Application','Tax Research Memo'],DIR.ADVANCED)],
        ], Q_CPA)

    # === Standalone Paths ===
    print('\n=== Standalone Paths ===')
    # Frontend Development (no semester)
    fe = cp('Frontend Development',
        'Master React, TypeScript, and modern frontend tooling.',
        [
            {'title':'React Essentials','lessons':['React Fundamentals','JSX and Components','Props and State','Event Handling','Conditional Rendering','Lists and Keys'],'quiz':Q_SE,'duration':10},
            {'title':'TypeScript','lessons':['TypeScript Setup','Basic Types','Interfaces','Generics','Enums','Type Narrowing'],'quiz':Q_SE,'duration':10},
            {'title':'State Management','lessons':['useState Deep Dive','useReducer','Context API','Zustand','Redux Toolkit','State Persistence'],'quiz':Q_SE,'duration':10},
            {'title':'Routing and Navigation','lessons':['React Router Setup','Route Configuration','Nested Routes','Route Guards','Lazy Loading','Navigation Patterns'],'quiz':Q_SE,'duration':10},
            {'title':'API Integration','lessons':['Fetch API','Axios Setup','REST APIs','GraphQL Basics','Error Handling','Loading States'],'quiz':Q_SE,'duration':10},
            {'title':'Testing and Deployment','lessons':['Unit Testing','Integration Testing','E2E Testing','Build and Deploy','CI/CD','Performance'],'quiz':Q_SE,'duration':10},
            {'title':'Project: Frontend Application','lessons':['Project Planning','Component Architecture','State Design','API Integration','Testing','Deployment'],'quiz':Q_SE,'duration':10},
        ],
        semester=None, difficulty=DIR.INTERMEDIATE)
    print(f'  Frontend Development (id={fe.id})')

    be = cp('Backend Development',
        'Build robust APIs and server-side systems with Django and Python.',
        [
            {'title':'Django Fundamentals','lessons':['Django Setup','Models and ORM','Views and URLs','Templates','Admin Interface','Migrations'],'quiz':Q_SE,'duration':10},
            {'title':'REST API Design','lessons':['REST Principles','DRF Serializers','ViewSets','Authentication','Permissions','Versioning'],'quiz':Q_SE,'duration':10},
            {'title':'Database Design','lessons':['Schema Design','Relationships','Query Optimisation','Migrations','Seeding','Indexing'],'quiz':Q_SE,'duration':10},
            {'title':'Authentication and Security','lessons':['JWT Auth','OAuth2','Password Hashing','CSRF Protection','Rate Limiting','Security Best Practices'],'quiz':Q_SE,'duration':10},
            {'title':'Testing and CI/CD','lessons':['Unit Testing','Integration Testing','Docker Setup','CI/CD Pipeline','Deployment','Monitoring'],'quiz':Q_SE,'duration':10},
            {'title':'Advanced Topics','lessons':['Caching','Background Tasks','WebSockets','File Uploads','API Documentation','Logging'],'quiz':Q_SE,'duration':10},
            {'title':'Project: Backend System','lessons':['System Design','Model Architecture','API Development','Auth Implementation','Testing','Deployment'],'quiz':Q_SE,'duration':10},
        ],
        semester=None, difficulty=DIR.INTERMEDIATE)
    print(f'  Backend Development (id={be.id})')

    print(f'\n=== GLOBAL SUMMARY ===')
    print(f'Programs: {Program.objects.count()}')
    print(f'Semesters: {Semester.objects.count()}')
    print(f'LearningPaths: {LearningPath.objects.count()}')
    print(f'Modules: {Module.objects.count()}')
    print(f'Lessons: {Lesson.objects.count()}')

if __name__ == '__main__':
    main()
