# LMS Platform

Full-stack Learning Management System — **Django REST Framework** backend + **React (TypeScript)** frontend with **Tailwind CSS**.

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 5.0, Django REST Framework, SimpleJWT, PostgreSQL |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Zustand |
| **Database** | PostgreSQL |

## Project Structure

```
lms/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── lms_project/          # Django project config
│   │   ├── settings.py
│   │   └── urls.py
│   ├── accounts/             # User model, auth, permissions
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py          # Register, Login, Me
│   │   ├── views_admin.py    # Admin: user list, verify instructor
│   │   ├── permissions.py
│   │   └── urls.py
│   ├── learning/             # Paths, Modules, Lessons
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py          # ViewSets + custom actions
│   │   └── urls.py
│   └── enrollment/           # Enrollments, Lesson Completions
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx            # Router + role-based guards
        ├── api/client.ts      # Axios instance w/ JWT interceptor
        ├── stores/            # Zustand stores (auth, paths, player)
        ├── types/index.ts     # Shared TypeScript interfaces
        └── pages/             # Page components
            ├── LoginPage.tsx
            ├── RegisterPage.tsx
            ├── LearnerDashboard.tsx
            ├── PathDetailPage.tsx
            ├── CoursePlayerPage.tsx   ← Core UX
            ├── InstructorDashboard.tsx
            ├── InstructorPathEditor.tsx
            ├── InstructorAnalytics.tsx
            └── AdminDashboard.tsx
```

## Database Schema

| Table | Model | Purpose |
|---|---|---|
| `users` | `accounts.User` | Custom user (AbstractUser) with role field |
| `learning_paths` | `learning.LearningPath` | Course containers (DRAFT/PUBLISHED/ARCHIVED) |
| `path_prerequisites` | `learning.PathPrerequisite` | M2M prerequisite links between paths |
| `modules` | `learning.Module` | Ordered groupings within a path |
| `lessons` | `learning.Lesson` | Content items (VIDEO / MARKDOWN / QUIZ) |
| `enrollments` | `enrollment.Enrollment` | User-to-path enrollment with progress properties |
| `lesson_completions` | `enrollment.LessonCompletion` | Per-user lesson completion records |

**Progress calculation**: `completed_lessons / total_published_lessons * 100`, computed as a property on the `Enrollment` model.

## API Endpoints

### Auth
| Method | Path | Permission |
|---|---|---|
| POST | `/api/auth/register/` | AllowAny |
| POST | `/api/auth/login/` | AllowAny |
| GET | `/api/auth/me/` | IsAuthenticated |
| POST | `/api/auth/refresh/` | AllowAny |

### Learning Paths
| Method | Path | Permission |
|---|---|---|
| GET | `/api/paths/` | IsAuthenticated |
| GET | `/api/paths/{id}/` | IsAuthenticated |
| POST | `/api/paths/{id}/enroll/` | IsAuthenticated |
| GET/POST | `/api/instructor/paths/` | IsInstructorOrAdmin |
| PUT/PATCH | `/api/instructor/paths/{id}/` | IsInstructorOrAdmin |
| GET | `/api/instructor/paths/analytics/` | IsInstructorOrAdmin |

### Lessons
| Method | Path | Permission |
|---|---|---|
| GET | `/api/lessons/{id}/` | IsAuthenticated |
| POST | `/api/lessons/{id}/complete/` | IsAuthenticated |
| POST | `/api/lessons/` | IsInstructorOrAdmin |
| PUT/PATCH/DELETE | `/api/lessons/{id}/` | IsInstructorOrAdmin |

### Enrollments
| Method | Path | Permission |
|---|---|---|
| GET | `/api/enrollments/` | IsAuthenticated |
| POST | `/api/enrollments/create/` | IsAuthenticated |
| GET | `/api/enrollments/{path_id}/progress/` | IsAuthenticated |

### Admin
| Method | Path | Permission |
|---|---|---|
| GET | `/api/admin/users/` | IsAdmin |
| PUT | `/api/admin/instructors/{id}/verify/` | IsAdmin |

## UI Component Tree

```
App (React Router)
├── /login          → LoginPage
├── /register       → RegisterPage
├── /               → LearnerDashboard
│   ├── EnrolledPathCard (progress bar)
│   └── ExplorePathCard (discovery grid)
├── /paths/:id      → PathDetailPage
│   ├── Path header + metadata + enroll CTA
│   └── Module accordion → LessonRow (status icons)
├── /paths/:pathId/lessons/:lessonId  → CoursePlayerPage  ← Core UX
│   ├── Sidebar (collapsible, 320px)
│   │   ├── Progress bar
│   │   └── Module sections → Lesson links (status dots)
│   └── Content area
│       ├── Video / Markdown / Quiz renderer
│       └── Navigation (Previous | Complete & Continue)
│   └── Bottom progress bar (1px)
├── /instructor                    → InstructorDashboard
├── /instructor/paths/:id?        → InstructorPathEditor
├── /instructor/analytics         → InstructorAnalytics
└── /admin                        → AdminDashboard (user mgmt)
```

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+

### Backend

```powershell
cd backend

# Create virtual environment & install deps
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
# Edit .env with your PostgreSQL credentials

# Run migrations & seed
python manage.py migrate
python manage.py createsuperuser

# Start dev server
python manage.py runserver
```

The API server starts on `http://localhost:8000`. `http://127.0.0.1:8000/admin/`

### Frontend

```powershell
cd frontend

npm install
npm run dev
```

The dev server starts on `http://localhost:5173` (proxies `/api` to the Django backend).

## Key Design Decisions

- **`lesson_completions` join table** enables precise per-user progress tracking without polluting lesson metadata
- **JWT auth** via SimpleJWT with `Bearer` tokens; Axios interceptor auto-attaches and handles 401s
- **`Enrollment.progress_percent`** as a computed property (completed / total published lessons)
- **Role-based access** enforced at both the API (DRF permissions) and UI (React Router guards)
- **Distraction-free player** — sidebar collapses, minimal chrome during lessons (Coursera-inspired)
- **Zustand** for lightweight state management without boilerplate (auth, paths, player stores)
