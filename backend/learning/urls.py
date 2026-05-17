from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"programs", views.ProgramViewSet, basename="program")
router.register(r"semesters", views.SemesterViewSet, basename="semester")
router.register(r"paths", views.LearningPathViewSet, basename="path")
router.register(r"instructor/paths", views.InstructorPathViewSet, basename="instructor-path")
router.register(r"modules", views.ModuleViewSet, basename="module")
router.register(r"lessons", views.LessonViewSet, basename="lesson")

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/<int:lesson_pk>/questions/", views.QuestionViewSet.as_view({"get": "list"}), name="lesson-questions"),
    path("lessons/<int:lesson_pk>/ai-instruct/", views.AIInstructView.as_view(), name="lesson-ai-instruct"),
]
