import os, json, re
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_project.settings'
import django; django.setup()
from learning.models import Lesson

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_content.json"), encoding="utf-8") as f:
    pdfs = json.load(f)

def clean_pdf(text):
    lines = text.split("\n")
    out = []
    skip = True
    for line in lines:
        s = line.strip()
        if skip:
            if s.startswith("LESSON") or "Learning outcomes" in s:
                skip = False
                out.append(line)
            continue
        if (s.startswith("JKUAT: Setting") or s.startswith("JKUAT SODeL") or
            s.startswith("JOMO KENYATTA") or "P.O. Box" in s or "E-mail:" in s or
            s.startswith("ICS 2203") or s.startswith("LAST REVISION") or
            s.startswith("This presentation") or s.startswith("The notes, examples") or
            s.startswith("Errors and omissions") or s.startswith("Back Close") or
            s.startswith("JJII") or s.startswith("JDocDocI") or s == "" or
            s.startswith("\x0c") or re.match(r'^\d+$', s)):
            continue
        out.append(line)
    return "\n".join(out).strip()

# Precise mapping: lesson title (exact match) → PDF key
direct_map = {
    "HTML": ("Lesson 6", None),
    "XHTML": ("Lesson 7", None),
    "XML": ("Lesson 8", None),
    "CSS": ("Lesson 9", None),
    "JavaScript": ("Lesson 10", None),
}

# First, fix the new lessons (DB#24-33)
for lesson in Lesson.objects.filter(title__in=list(direct_map.keys()), content_type="MARKDOWN"):
    pdf_key, _ = direct_map[lesson.title]
    raw = pdfs.get(pdf_key, "")
    if not raw:
        continue
    cleaned = clean_pdf(raw)
    lesson.content_body = cleaned[:50000]
    lesson.save()
    print(f"  {lesson.title} (DB#{lesson.id}): {len(cleaned)} chars from {pdf_key}")

# For the quiz lessons that got content_body set, clear it back
for lesson in Lesson.objects.filter(content_type="QUIZ"):
    quiz_topics = ["Internet & Networks", "Internet Architecture", "Distributed Web Technologies", "DNS", "Web Hosting",
                   "HTML Quiz", "XHTML Quiz", "XML Quiz", "CSS Quiz", "JavaScript Quiz"]
    if lesson.title in quiz_topics:
        lesson.content_body = ""
        lesson.save()
        print(f"  Cleared quiz: {lesson.title} (DB#{lesson.id})")

# Now update the existing lessons (DB#1-18) with relevant website_development.pdf content
wd = pdfs.get("Website Development", "")
if wd:
    # Split into sections by major headings
    sections = re.split(r'\n(?=[A-Z][a-z]+ [A-Z][a-z]+|\d+\.\s)', wd)
    section_map = {
        "What is Web Development": ["What is Web Development", "What is a Website"],
        "Before You Begin": ["Before You Begin", "Web Project"],
        "Business Goals": ["Business Goals"],
        "User Needs": ["User Needs"],
        "The Content Journey": ["Content Journey"],
        "Content Formats": ["Content Formats"],
        "The Website Design Process": ["Website Design Process"],
        "Information Architecture": ["Information Architecture"],
        "Interface, Navigation": ["Interface", "Navigation", "Information Design"],
        "Visual Design": ["Visual Design", "Usability"],
        "Browser Compatibility": ["Browser Compatibility"],
        "Screen Resolution": ["Screen Resolution", "Web Accessibility", "Accessibility"],
        "The Website Testing": ["Testing", "Test"],
        "Choosing a Host": ["Choosing a Host", "Host", "Domain"],
        "Service Level": ["Service Level", "SLA"],
        "Online Publicity": ["Online Publicity"],
        "Offline": ["Offline", "Intranet Publicity"],
        "Website Review": ["Review", "SWOT"],
    }
    for lesson in Lesson.objects.filter(content_type="MARKDOWN").order_by("module__sort_order", "sort_order"):
        if lesson.id > 18:
            continue
        keywords = section_map.get(lesson.title, [lesson.title])
        matches = []
        for sec in sections:
            sec_lower = sec.lower()
            if any(kw.lower() in sec_lower for kw in keywords):
                matches.append(sec)
        if matches:
            combined = "\n\n".join(matches)
            lesson.content_body = combined[:50000]
            lesson.save()
            print(f"  {lesson.title} (DB#{lesson.id}): {len(combined)} chars from Website Development")
        else:
            print(f"  {lesson.title} (DB#{lesson.id}): NO MATCH found")

print("\nDone!")
