from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q, Prefetch

from .models import Program, Semester, LearningPath, Module, Lesson, Question


class LargePagePagination(PageNumberPagination):
    page_size = 200
    page_size_query_param = 'page_size'
from .serializers import (
    ProgramSerializer,
    SemesterSerializer,
    LearningPathListSerializer,
    LearningPathDetailSerializer,
    ModuleSerializer,
    ModuleWriteSerializer,
    LessonSerializer,
    LessonDetailSerializer,
    LessonWriteSerializer,
    QuestionSerializer,
)
from accounts.permissions import IsInstructorOrAdmin


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    pagination_class = None

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        prog = self.get_object()
        from enrollment.models import Enrollment
        path_ids = list(LearningPath.objects.filter(semester__program=prog).values_list("id", flat=True))
        existing = set(Enrollment.objects.filter(
            user=request.user, learning_path_id__in=path_ids
        ).values_list("learning_path_id", flat=True))
        created = 0
        for pid in path_ids:
            if pid not in existing:
                Enrollment.objects.create(user=request.user, learning_path_id=pid)
                created += 1
        return Response({"enrolled": created, "total": len(path_ids)}, status=status.HTTP_201_CREATED)


class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SemesterSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Semester.objects.all()
        program_id = self.request.query_params.get("program")
        if program_id:
            qs = qs.filter(program_id=program_id)
        return qs


class LearningPathViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = LargePagePagination
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return LearningPathListSerializer
        return LearningPathDetailSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        qs = LearningPath.objects.filter(status=LearningPath.Status.PUBLISHED)
        if self.action == "list":
            from enrollment.models import Enrollment
            qs = qs.order_by('-created_at').select_related('instructor').annotate(
                _module_count=Count('modules', distinct=True),
                _lesson_count=Count('modules__lessons', distinct=True),
                _enrolled_count=Count('enrollments', distinct=True),
            ).prefetch_related(
                Prefetch('enrollments',
                    queryset=Enrollment.objects.filter(user=self.request.user).prefetch_related('completions'),
                    to_attr='_user_enrollments',
                ),
            )
        elif self.action == "retrieve":
            from enrollment.models import Enrollment, LessonCompletion
            qs = qs.select_related('instructor').prefetch_related(
                Prefetch('enrollments',
                    queryset=Enrollment.objects.filter(user=self.request.user).prefetch_related('completions'),
                    to_attr='_user_enrollments',
                ),
                Prefetch('modules',
                    queryset=Module.objects.order_by('sort_order').prefetch_related(
                        Prefetch('lessons',
                            queryset=Lesson.objects.filter(status=Lesson.Status.PUBLISHED).order_by('sort_order').prefetch_related(
                                Prefetch('lesson_completions',
                                    queryset=LessonCompletion.objects.filter(user=self.request.user),
                                    to_attr='_user_completions',
                                ),
                            ),
                        ),
                    ),
                ),
            )
        return qs

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        path = self.get_object()
        if path.enrollments.filter(user=request.user).exists():
            return Response({"error": "Already enrolled"}, status=status.HTTP_400_BAD_REQUEST)
        from enrollment.models import Enrollment
        Enrollment.objects.create(user=request.user, learning_path=path)
        return Response({"message": "Enrolled successfully"}, status=status.HTTP_201_CREATED)


class InstructorPathViewSet(viewsets.ModelViewSet):
    serializer_class = LearningPathDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrAdmin]

    def get_queryset(self):
        return LearningPath.objects.filter(instructor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=False)
    def analytics(self, request):
        paths = self.get_queryset().annotate(
            enrolled_count=Count("enrollments", distinct=True),
            completed_count=Count(
                "enrollments",
                filter=Q(enrollments__completed_at__isnull=False),
                distinct=True,
            ),
        )
        data = []
        for path in paths:
            data.append({
                "path_id": path.id,
                "path_title": path.title,
                "enrolled_count": path.enrolled_count,
                "completed_count": path.completed_count,
                "published": path.status == LearningPath.Status.PUBLISHED,
            })
        return Response(data)


class ModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrAdmin]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ModuleWriteSerializer
        return ModuleSerializer

    def get_queryset(self):
        return Module.objects.filter(learning_path__instructor=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return LessonWriteSerializer
        return LessonDetailSerializer if self.action == "retrieve" else LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ("INSTRUCTOR", "ADMIN"):
            return Lesson.objects.filter(module__learning_path__instructor=user)
        return Lesson.objects.filter(status=Lesson.Status.PUBLISHED)

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        if request.user.role not in ("INSTRUCTOR", "ADMIN"):
            path = lesson.module.learning_path
            ordered = Lesson.objects.filter(
                module__learning_path=path,
                status=Lesson.Status.PUBLISHED,
            ).order_by("module__sort_order", "sort_order")

            seen_current = False
            for prev in ordered:
                if prev.id == lesson.id:
                    seen_current = True
                    continue
                if not seen_current:
                    if not prev.lesson_completions.filter(user=request.user).exists():
                        return Response(
                            {"error": "Complete previous lessons first"},
                            status=status.HTTP_403_FORBIDDEN,
                        )
        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        from enrollment.models import LessonCompletion, Enrollment, Certificate
        from django.utils.crypto import get_random_string
        lesson = self.get_object()
        enrollment = Enrollment.objects.filter(
            user=request.user, learning_path=lesson.module.learning_path
        ).first()
        if not enrollment:
            return Response({"error": "Not enrolled"}, status=status.HTTP_400_BAD_REQUEST)
        _, created = LessonCompletion.objects.get_or_create(
            user=request.user, lesson=lesson, enrollment=enrollment
        )
        cert_id = None
        if enrollment.is_completed:
            cert, _ = Certificate.objects.get_or_create(
                user=request.user, learning_path=lesson.module.learning_path,
                defaults={"certificate_id": get_random_string(16).upper()},
            )
            cert_id = cert.certificate_id
        return Response({
            "lesson_id": lesson.id,
            "path_id": lesson.module.learning_path.id,
            "progress_percent": enrollment.progress_percent,
            "is_path_completed": enrollment.is_completed,
            "certificate_id": cert_id,
        })


class AIInstructView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_pk):
        from .models import Lesson
        from .ai_instructor import generate_response
        question = request.data.get('question', '').strip()
        if not question:
            return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            lesson = Lesson.objects.select_related('module__learning_path').get(id=lesson_pk)
        except Lesson.DoesNotExist:
            return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)
        result = generate_response(lesson, question)
        return Response(result)


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        lesson_id = self.kwargs.get("lesson_pk")
        if not lesson_id:
            return Question.objects.none()
        lesson = Lesson.objects.get(id=lesson_id)
        user = self.request.user
        if user.role not in ("INSTRUCTOR", "ADMIN"):
            ordered = Lesson.objects.filter(
                module__learning_path=lesson.module.learning_path,
                status=Lesson.Status.PUBLISHED,
            ).order_by("module__sort_order", "sort_order")
            seen_current = False
            for prev in ordered:
                if prev.id == lesson.id:
                    seen_current = True
                    continue
                if not seen_current:
                    if not prev.lesson_completions.filter(user=user).exists():
                        raise PermissionDenied("Complete previous lessons first")

            module_lessons = Lesson.objects.filter(
                module=lesson.module,
                status=Lesson.Status.PUBLISHED,
            ).exclude(content_type="QUIZ")
            has_all_content_completed = all(
                ml.lesson_completions.filter(user=user).exists()
                for ml in module_lessons
            )
            if not has_all_content_completed:
                return Question.objects.none()
        return Question.objects.filter(lesson=lesson)
