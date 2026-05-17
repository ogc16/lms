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

Q_COMMERCE = [
    {'text':'Which of the following is a factor of production?','a':'Money','b':'Land','c':'Bonds','d':'Stocks','correct':'b'},
    {'text':'The law of demand states that price and quantity demanded are:','a':'Directly related','b':'Inversely related','c':'Unrelated','d':'Proportionally equal','correct':'b'},
    {'text':'What is opportunity cost?','a':'Money spent on a purchase','b':'Value of the next best alternative forgone','c':'Total cost of production','d':'Marginal cost','correct':'b'},
    {'text':'GDP measures:','a':'Government debt','b':'Total value of goods and services produced','c':'National savings','d':'Stock market performance','correct':'b'},
    {'text':'Which market structure has many sellers with differentiated products?','a':'Perfect competition','b':'Monopolistic competition','c':'Oligopoly','d':'Monopoly','correct':'b'},
    {'text':'The central bank controls inflation primarily through:','a':'Fiscal policy','b':'Monetary policy','c':'Trade policy','d':'Industrial policy','correct':'b'},
    {'text':'A budget deficit occurs when:','a':'Revenue exceeds expenditure','b':'Expenditure exceeds revenue','c':'Exports exceed imports','d':'Savings exceed investment','correct':'b'},
    {'text':'Comparative advantage means:','a':'Producing at lower absolute cost','b':'Producing at lower opportunity cost','c':'Producing more output','d':'Producing higher quality','correct':'b'},
    {'text':'Elasticity measures:','a':'Market size','b':'Responsiveness of quantity to price changes','c':'Profit margins','d':'Production efficiency','correct':'b'},
    {'text':'Which is NOT a type of unemployment?','a':'Frictional','b':'Structural','c':'Cyclical','d':'Operational','correct':'d'},
]

Q_FINANCE = [
    {'text':'NPV stands for:','a':'Net Present Value','b':'Net Profit Variance','c':'Nominal Present Value','d':'Negotiated Payment Value','correct':'a'},
    {'text':'The capital asset pricing model (CAPM) calculates:','a':'Expected return based on systematic risk','b':'Total portfolio variance','c':'Company market value','d':'Dividend yield','correct':'a'},
    {'text':'A bond\'s yield to maturity is:','a':'Coupon rate divided by price','b':'Total return if held to maturity','c':'Current yield plus capital gain','d':'Face value minus price','correct':'b'},
    {'text':'Derivatives are primarily used for:','a':'Raising capital','b':'Hedging risk','c':'Increasing dividends','d':'Reducing taxes','correct':'b'},
    {'text':'The efficient market hypothesis suggests:','a':'Markets always overvalue stocks','b':'Asset prices reflect all available information','c':'Technical analysis always works','d':'Fundamental analysis is useless','correct':'b'},
    {'text':'WACC represents:','a':'Weighted average cost of capital','b':'Working capital','c':'Weighted asset calculation','d':'World-adjusted cost','correct':'a'},
    {'text':'Which ratio measures profitability?','a':'Current ratio','b':'Return on equity','c':'Debt-to-equity','d':'Asset turnover','correct':'b'},
    {'text':'Time value of money is based on:','a':'Inflation only','b':'Opportunity cost of waiting','c':'Risk-free rate only','d':'Market volatility','correct':'b'},
    {'text':'IPO stands for:','a':'Internal Purchase Order','b':'Initial Public Offering','c':'Investment Portfolio Option','d':'Interest Payment Obligation','correct':'b'},
    {'text':'Systematic risk is also known as:','a':'Diversifiable risk','b':'Market risk','c':'Firm-specific risk','d':'Idiosyncratic risk','correct':'b'},
]

Q_PM = [
    {'text':'What is the triple constraint of project management?','a':'Time, Cost, Quality','b':'Scope, Time, Cost','c':'Quality, Risk, Resources','d':'Scope, Quality, Customer','correct':'b'},
    {'text':'Work Breakdown Structure (WBS) is:','a':'A project schedule','b':'Hierarchical decomposition of work','c':'A risk register','d':'A communication plan','correct':'b'},
    {'text':'Critical path is:','a':'The shortest path in the network','b':'The longest path determining project duration','c':'The path with most resources','d':'The path with highest risk','correct':'b'},
    {'text':'Earned Value Management compares:','a':'Actual vs planned progress and cost','b':'Revenue vs expenses','c':'Profit vs loss','d':'Scope vs quality','correct':'a'},
    {'text':'In Agile, a sprint typically lasts:','a':'1 day','b':'1-4 weeks','c':'6 months','d':'1 year','correct':'b'},
    {'text':'Risk mitigation involves:','a':'Ignoring risks','b':'Reducing probability or impact','c':'Transferring all risk','d':'Accepting all risks','correct':'b'},
    {'text':'RACI matrix is used for:','a':'Budget allocation','b':'Role and responsibility assignment','c':'Risk identification','d':'Resource levelling','correct':'b'},
    {'text':'What is a project stakeholder?','a':'Only the project sponsor','b':'Anyone affected by the project','c':'Only the project team','d':'External auditors only','correct':'b'},
    {'text':'Milestone in a project is:','a':'A major task','b':'A significant event or checkpoint','c':'The project budget','d':'The final deliverable','correct':'b'},
    {'text':'Which process group comes first?','a':'Planning','b':'Initiating','c':'Executing','d':'Monitoring and Controlling','correct':'b'},
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
    # === Bachelor of Commerce ===
    add_program('Bachelor of Commerce',
        'A comprehensive four-year degree covering economics, accounting, finance, marketing, management, and business strategy.',
        ['Year 1 Semester 1','Year 1 Semester 2','Year 2 Semester 1','Year 2 Semester 2','Year 3 Semester 1','Year 3 Semester 2','Year 4 Semester 1','Year 4 Semester 2'],
        [
            [('Principles of Economics','Supply, demand, market equilibrium, and economic systems.',['Economic Fundamentals','Supply and Demand','Market Equilibrium','Elasticity','Consumer Choice','Market Structures'],'Economics',['Market Analysis','Elasticity Calculation','Consumer Choice Model','Market Structure Report'],DIR.BEGINNER),
             ('Financial Accounting I','Accounting principles, double entry, financial statements.',['Accounting Principles','Double Entry System','Trial Balance','Financial Statements','Adjusting Entries','Closing Process'],'Accounting',['Journal Entries','Trial Balance Prep','Statement Preparation','Closing Entries'],DIR.BEGINNER),
             ('Business Mathematics','Mathematics for business: algebra, calculus, financial maths.',['Algebra Review','Linear Functions','Quadratic Functions','Calculus Basics','Financial Mathematics','Statistics Introduction'],'Business Math',['Function Analysis','Calculus Applications','Financial Calculations','Statistical Analysis'],DIR.BEGINNER),
             ('Communication Skills','Business writing, presentations, interpersonal communication.',['Business Writing','Report Preparation','Presentation Skills','Negotiation','Cross-Cultural Communication','Digital Communication'],'Communication',['Business Letter','Report Writing','Presentation','Negotiation Simulation'],DIR.BEGINNER)],
            [('Microeconomics','Consumer theory, production, costs, perfect competition.',['Consumer Theory','Production Function','Cost Curves','Perfect Competition','Monopoly','Market Failures'],'Microeconomics',['Consumer Analysis','Production Analysis','Cost Analysis','Market Structure Report'],DIR.INTERMEDIATE),
             ('Financial Accounting II','Partnerships, companies, cash flow, financial analysis.',['Partnership Accounting','Company Accounting','Statement of Cash Flows','Financial Analysis','Accounting Standards','Ethics in Accounting'],'Accounting II',['Partnership Reports','Cash Flow Statement','Ratio Analysis','Ethics Case Study'],DIR.INTERMEDIATE),
             ('Business Statistics','Descriptive statistics, probability, sampling, hypothesis testing.',['Descriptive Statistics','Probability Distributions','Sampling','Estimation','Hypothesis Testing','Regression'],'Statistics',['Descriptive Analysis','Probability Calculations','Sampling Exercise','Hypothesis Test'],DIR.INTERMEDIATE),
             ('Commercial Law','Contracts, sale of goods, agency, business organisations.',['Legal System','Contract Law','Sale of Goods','Agency Law','Partnership Law','Company Law'],'Commercial Law',['Contract Analysis','Case Study','Agency Problem','Company Formation'],DIR.INTERMEDIATE)],
            [('Macroeconomics','National income, inflation, unemployment, fiscal policy.',['National Income','Aggregate Demand','Fiscal Policy','Money and Banking','Inflation','Unemployment'],'Macroeconomics',['GDP Calculation','Fiscal Analysis','Monetary Policy','Inflation Analysis'],DIR.INTERMEDIATE),
             ('Management Accounting','Costing, budgeting, variance analysis, decision making.',['Cost Classification','Job Costing','Process Costing','Budgeting','Variance Analysis','Decision Making'],'Management Accounting',['Cost Analysis','Budget Preparation','Variance Report','Decision Analysis'],DIR.INTERMEDIATE),
             ('Marketing Principles','Marketing mix, segmentation, targeting, positioning.',['Marketing Concepts','STP Framework','Product Strategy','Pricing Strategy','Distribution Channels','Promotion Strategy'],'Marketing',['STP Analysis','Product Plan','Pricing Strategy','Marketing Mix'],DIR.INTERMEDIATE),
             ('Organisational Behaviour','Individual behaviour, motivation, teams, culture.',['Individual Differences','Motivation','Group Dynamics','Team Effectiveness','Organisational Culture','Change Management'],'Organisational Behaviour',['Motivation Assessment','Team Analysis','Culture Diagnosis','Change Plan'],DIR.INTERMEDIATE)],
            [('Intermediate Microeconomics','Game theory, oligopoly, externalities, public goods.',['Game Theory','Oligopoly','Externalities','Public Goods','Asymmetric Information','Welfare Economics'],'Microeconomics',['Game Theory Analysis','Oligopoly Model','Externality Case','Welfare Analysis'],DIR.INTERMEDIATE),
             ('Corporate Accounting','Consolidation, group accounts, goodwill.',['Group Structures','Consolidation','Goodwill','Minority Interest','Associates','Group Cash Flow'],'Corporate Accounting',['Consolidation Worksheet','Goodwill Calculation','Group Statements','Cash Flow Analysis'],DIR.ADVANCED),
             ('Marketing Management','Branding, consumer behaviour, digital marketing.',['Brand Management','Consumer Behaviour','Market Research','Digital Marketing','Social Media Marketing','Marketing Analytics'],'Marketing Management',['Brand Strategy','Consumer Analysis','Market Research','Digital Campaign'],DIR.ADVANCED),
             ('Human Resource Management','Recruitment, training, performance, compensation.',['HR Planning','Recruitment','Training','Performance Management','Compensation','Employee Relations'],'HR',['Workforce Plan','Recruitment Process','Training Programme','Performance System'],DIR.INTERMEDIATE)],
            [('Econometrics','Regression analysis, hypothesis testing, forecasting.',['Econometric Methods','Simple Regression','Multiple Regression','Hypothesis Testing','Time Series','Forecasting'],'Econometrics',['Regression Analysis','Hypothesis Test','Time Series Model','Forecast'],DIR.ADVANCED),
             ('Advanced Financial Accounting','Complex financial instruments, leases, revenue recognition.',['Financial Instruments','Lease Accounting','Revenue Recognition','Deferred Tax','Earnings Per Share','Segment Reporting'],'Advanced Accounting',['Instrument Valuation','Lease Calculation','Revenue Analysis','Comprehensive Statements'],DIR.ADVANCED),
             ('Consumer Behaviour','Psychological and social factors, decision process.',['Consumer Psychology','Social Influences','Decision Process','Attitudes','Culture','Digital Consumer'],'Consumer Behaviour',['Psychology Analysis','Social Impact Study','Decision Process','Digital Consumer Report'],DIR.ADVANCED),
             ('Investment Analysis','Portfolio theory, asset pricing, equity valuation.',['Portfolio Theory','Risk and Return','CAPM','Equity Valuation','Bond Valuation','Portfolio Management'],'Investment Analysis',['Portfolio Construction','Risk Assessment','Valuation','Portfolio Review'],DIR.ADVANCED)],
            [('International Economics','Trade theory, balance of payments, exchange rates.',['Trade Theories','Trade Policy','Balance of Payments','Exchange Rates','International Capital','Global Institutions'],'International Economics',['Trade Analysis','Policy Assessment','Balance of Payments','Exchange Rate Analysis'],DIR.ADVANCED),
             ('Auditing','Audit process, evidence, internal control, reporting.',['Audit Framework','Audit Planning','Audit Evidence','Internal Control','Audit Sampling','Audit Reporting'],'Auditing',['Audit Plan','Control Assessment','Sampling','Audit Report'],DIR.ADVANCED),
             ('Entrepreneurship','Opportunity, business planning, financing, growth.',['Entrepreneurial Process','Opportunity Recognition','Business Model','Business Planning','Financing','Growth Strategies'],'Entrepreneurship',['Business Model Canvas','Business Plan','Financial Projections','Pitch Deck'],DIR.ADVANCED),
             ('Strategic Management','Strategy formulation, competitive advantage, execution.',['Strategy Concepts','Environmental Analysis','Internal Analysis','Strategy Formulation','Strategy Implementation','Strategy Evaluation'],'Strategy',['External Analysis','Internal Audit','Strategy Proposal','Implementation Plan'],DIR.ADVANCED)],
            [('Public Finance','Government revenue, taxation, public expenditure.',['Public Finance Overview','Taxation Principles','Tax Structures','Public Expenditure','Fiscal Federalism','Budget Analysis'],'Public Finance',['Tax Analysis','Expenditure Review','Fiscal Analysis','Budget Evaluation'],DIR.ADVANCED),
             ('Taxation','Income tax, corporation tax, VAT, tax planning.',['Tax System','Income Tax','Corporation Tax','VAT','Capital Gains','Tax Planning'],'Taxation',['Tax Computation','Corporate Tax','VAT Return','Tax Planning'],DIR.ADVANCED),
             ('Supply Chain Management','Logistics, procurement, inventory, operations.',['SCM Overview','Logistics','Procurement','Inventory Management','Operations Strategy','Sustainable SCM'],'Supply Chain',['Logistics Design','Procurement Strategy','Inventory Analysis','Sustainability Plan'],DIR.ADVANCED),
             ('Business Research Methods','Research design, data collection, analysis, reporting.',['Research Design','Literature Review','Data Collection','Data Analysis','Qualitative Methods','Research Ethics'],'Research Methods',['Research Proposal','Literature Review','Data Collection','Research Report'],DIR.ADVANCED)],
            [('Development Economics','Economic development, poverty, growth strategies.',['Development Concepts','Growth Theories','Poverty and Inequality','Human Capital','Institutions','Development Policy'],'Development Economics',['Growth Analysis','Poverty Assessment','Human Capital Analysis','Policy Proposal'],DIR.ADVANCED),
             ('Capstone: Business Strategy','Integrative business project: analysis to implementation.',['Strategic Analysis','Market Research','Financial Planning','Implementation Strategy','Risk Management','Presentation'],'Business Capstone',['Strategic Analysis','Market Research','Financial Plan','Final Presentation'],DIR.ADVANCED)],
        ], Q_COMMERCE)

    # === MSc Finance ===
    add_program('MSc Finance',
        'An advanced one-year masters programme in finance covering corporate finance, investments, financial modelling, and risk management.',
        ['Semester 1','Semester 2'],
        [
            [('Corporate Finance','Advanced capital budgeting, capital structure, dividend policy.',['Capital Budgeting','Cost of Capital','Capital Structure','Dividend Policy','Mergers and Acquisitions','Corporate Restructuring'],'Corporate Finance',['Budgeting Analysis','WACC Calculation','Capital Structure','M&A Valuation'],DIR.ADVANCED),
             ('Investment Analysis','Portfolio theory, asset allocation, performance evaluation.',['Modern Portfolio Theory','Asset Allocation','Fixed Income','Equity Analysis','Derivatives','Portfolio Performance'],'Investment Analysis',['Portfolio Construction','Fixed Income Analysis','Equity Valuation','Performance Report'],DIR.ADVANCED),
             ('Financial Modelling','Excel modelling, forecasting, valuation, scenario analysis.',['Excel Fundamentals','Financial Modelling','Forecasting','DCF Valuation','LBO Modelling','Scenario Analysis'],'Financial Modelling',['Model Design','DCF Model','LBO Model','Scenario Analysis'],DIR.ADVANCED),
             ('Derivatives and Risk Management','Options, futures, swaps, VaR, hedging strategies.',['Options','Futures and Forwards','Swaps','Option Strategies','VaR','Hedging Strategies'],'Derivatives',['Option Pricing','Futures Analysis','Swap Valuation','VaR Calculation'],DIR.ADVANCED)],
            [('International Finance','Exchange rates, international capital markets, FDI.',['Exchange Rate Theories','International Parity','International Capital Markets','Foreign Direct Investment','Country Risk','International Portfolio'],'International Finance',['Exchange Rate Analysis','Parity Check','Market Analysis','Country Risk Assessment'],DIR.ADVANCED),
             ('Advanced Financial Analysis','Financial statements analysis, credit analysis, valuation.',['Financial Analysis','Credit Analysis','Valuation Methods','ESG Analysis','Behavioural Finance','Financial Crises'],'Advanced Finance',['Financial Analysis','Credit Risk','Valuation Model','ESG Report'],DIR.ADVANCED),
             ('Fintech and Innovation','Blockchain, AI in finance, payments, regulatory tech.',['Fintech Overview','Blockchain in Finance','AI and Machine Learning','Digital Payments','RegTech','Future of Finance'],'Fintech',['Blockchain Analysis','AI Application','Payment System Design','RegTech Proposal'],DIR.ADVANCED),
             ('Capstone: Finance Project','Applied research project in finance.',['Project Proposal','Literature Review','Data Collection','Analysis','Recommendations','Presentation'],'Finance Capstone',['Research Proposal','Data Analysis','Recommendations','Final Presentation'],DIR.ADVANCED)],
        ], Q_FINANCE)

    # === MSc Project Management ===
    add_program('MSc Project Management',
        'An advanced one-year masters programme in project management covering PMBOK, Agile, risk, leadership, and strategic alignment.',
        ['Semester 1','Semester 2'],
        [
            [('Project Management Fundamentals','PMBOK, project life cycle, integration management.',['PMBOK Framework','Project Life Cycle','Integration Management','Scope Management','Schedule Management','Cost Management'],'PM Fundamentals',['Project Charter','WBS','Schedule Development','Cost Estimation'],DIR.ADVANCED),
             ('Agile and Scrum','Agile principles, Scrum framework, sprint management.',['Agile Manifesto','Scrum Framework','Sprint Planning','Daily Scrum','Sprint Review','Retrospectives'],'Agile',['Product Backlog','Sprint Plan','Scrum Simulation','Retrospective'],DIR.ADVANCED),
             ('Risk Management','Risk identification, analysis, response, monitoring.',['Risk Framework','Risk Identification','Risk Analysis','Risk Response','Risk Monitoring','Enterprise Risk Management'],'Risk Management',['Risk Register','Qualitative Analysis','Quantitative Analysis','Risk Response Plan'],DIR.ADVANCED),
             ('Project Leadership and Teams','Leadership styles, team dynamics, communication.',['Leadership Theories','Emotional Intelligence','Team Development','Conflict Resolution','Stakeholder Management','Communication Plan'],'Leadership',['Leadership Assessment','Team Analysis','Conflict Resolution','Communication Plan'],DIR.ADVANCED)],
            [('Advanced Project Management','Program management, portfolio management, PMO.',['Program Management','Portfolio Management','PMO Setup','Benefits Management','Governance','Maturity Models'],'Advanced PM',['Program Charter','Portfolio Analysis','PMO Design','Maturity Assessment'],DIR.ADVANCED),
             ('PMP Exam Preparation','Exam strategies, knowledge areas, practice tests.',['Exam Overview','Process Groups','Knowledge Areas','Formulas','Practice Tests','Exam Strategy'],'PMP Prep',['Knowledge Area Review','Formula Practice','Mock Exam','Study Plan'],DIR.ADVANCED),
             ('Digital Transformation and Projects','Digital strategy, AI in PM, change management.',['Digital Strategy','AI in Project Management','Change Management','Agile at Scale','Remote Teams','Digital Tools'],'Digital PM',['Digital Strategy','AI Application','Change Plan','Tool Evaluation'],DIR.ADVANCED),
             ('Capstone: Project Management Project','Comprehensive project applying PM methodologies.',['Project Proposal','Planning','Execution','Monitoring','Closure','Reflection'],'PM Capstone',['Project Charter','Project Plan','Status Reports','Lessons Learned'],DIR.ADVANCED)],
        ], Q_PM)

    print(f'\n=== GLOBAL SUMMARY ===')
    print(f'Programs: {Program.objects.count()}')
    print(f'Semesters: {Semester.objects.count()}')
    print(f'LearningPaths: {LearningPath.objects.count()}')
    print(f'Modules: {Module.objects.count()}')
    print(f'Lessons: {Lesson.objects.count()}')

if __name__ == '__main__':
    main()
