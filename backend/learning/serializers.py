from rest_framework import serializers
from .models import Program, Semester, LearningPath, Module, Lesson, Question


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ("id", "title", "description", "created_at")


class SemesterSerializer(serializers.ModelSerializer):
    program_title = serializers.CharField(source="program.title", read_only=True)

    class Meta:
        model = Semester
        fields = ("id", "program", "program_title", "year_number", "semester_number", "name", "created_at")


class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id", "module", "title", "description", "content_type",
            "content_url", "content_body", "duration_minutes", "status",
            "sort_order", "is_completed", "created_at", "updated_at",
        )
        read_only_fields = ("id", "is_completed", "created_at", "updated_at")

    def get_is_completed(self, obj):
        completions = getattr(obj, '_user_completions', None)
        if completions is not None:
            return len(completions) > 0
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.lesson_completions.filter(user=request.user).exists()
        return False


class LessonListSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id", "module", "title", "description", "content_type",
            "content_url", "duration_minutes", "status",
            "sort_order", "is_completed", "created_at", "updated_at",
        )
        read_only_fields = ("id", "is_completed", "created_at", "updated_at")

    def get_is_completed(self, obj):
        completions = getattr(obj, '_user_completions', None)
        if completions is not None:
            return len(completions) > 0
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.lesson_completions.filter(user=request.user).exists()
        return False


class LessonDetailSerializer(LessonSerializer):
    next_lesson_id = serializers.SerializerMethodField()
    previous_lesson_id = serializers.SerializerMethodField()

    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + ("next_lesson_id", "previous_lesson_id")

    def get_next_lesson_id(self, obj):
        next_lesson = (
            Lesson.objects.filter(
                module__learning_path=obj.module.learning_path,
                sort_order__gt=obj.sort_order,
                status=Lesson.Status.PUBLISHED,
            )
            .order_by("sort_order")
            .first()
        )
        return next_lesson.id if next_lesson else None

    def get_previous_lesson_id(self, obj):
        prev_lesson = (
            Lesson.objects.filter(
                module__learning_path=obj.module.learning_path,
                sort_order__lt=obj.sort_order,
                status=Lesson.Status.PUBLISHED,
            )
            .order_by("-sort_order")
            .first()
        )
        return prev_lesson.id if prev_lesson else None


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ("id", "learning_path", "title", "description", "sort_order", "lessons", "created_at", "updated_at")
        read_only_fields = ("id", "lessons", "created_at", "updated_at")


class LearningPathListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    module_count = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()
    enrolled_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    semester_id = serializers.SerializerMethodField()
    semester_name = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = (
            "id", "title", "description", "cover_image_url", "difficulty",
            "estimated_hours", "status", "instructor_name", "module_count",
            "lesson_count", "enrolled_count", "is_enrolled", "progress_percent",
            "semester_id", "semester_name",
        )

    def get_semester_id(self, obj):
        return obj.semester_id

    def get_semester_name(self, obj):
        return str(obj.semester) if obj.semester else None

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.email

    def get_module_count(self, obj):
        return getattr(obj, '_module_count', None) or obj.modules.count()

    def get_lesson_count(self, obj):
        return getattr(obj, '_lesson_count', None) or Lesson.objects.filter(module__learning_path=obj).count()

    def get_enrolled_count(self, obj):
        return getattr(obj, '_enrolled_count', None) or obj.enrollments.count()

    def get_is_enrolled(self, obj):
        enrollments = getattr(obj, '_user_enrollments', None)
        if enrollments is not None:
            return len(enrollments) > 0
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(user=request.user).exists()
        return False

    def get_progress_percent(self, obj):
        enrollments = getattr(obj, '_user_enrollments', None)
        if enrollments is not None:
            if enrollments:
                total = getattr(obj, '_lesson_count', None)
                if total is None:
                    total = Lesson.objects.filter(module__learning_path=obj).count()
                if total == 0:
                    return 0.0
                completed = enrollments[0].completions.count()
                return round((completed / total) * 100, 1)
            return 0.0
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            enrollment = obj.enrollments.filter(user=request.user).first()
            if enrollment:
                return enrollment.progress_percent
        return 0.0


class LearningPathDetailSerializer(serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()
    prerequisites = LearningPathListSerializer(many=True, read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = (
            "id", "title", "description", "cover_image_url", "difficulty",
            "estimated_hours", "status", "instructor", "prerequisites",
            "modules", "is_enrolled", "progress_percent", "created_at", "updated_at",
        )

    def get_instructor(self, obj):
        from accounts.serializers import UserSerializer
        return UserSerializer(obj.instructor).data

    def get_is_enrolled(self, obj):
        enrollments = getattr(obj, '_user_enrollments', None)
        if enrollments is not None:
            return len(enrollments) > 0
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(user=request.user).exists()
        return False

    def get_progress_percent(self, obj):
        enrollments = getattr(obj, '_user_enrollments', None)
        if enrollments is not None:
            if enrollments:
                lesson_qs = Lesson.objects.filter(
                    module__learning_path=obj,
                    status=Lesson.Status.PUBLISHED,
                )
                total = lesson_qs.count()
                if total == 0:
                    return 0.0
                completed = enrollments[0].completions.count()
                return round((completed / total) * 100, 1)
            return 0.0
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            enrollment = obj.enrollments.filter(user=request.user).first()
            if enrollment:
                return enrollment.progress_percent
        return 0.0


class ModuleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("id", "learning_path", "title", "description", "sort_order")


class LessonWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id", "module", "title", "description", "content_type",
            "content_url", "content_body", "duration_minutes", "status", "sort_order",
        )


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id", "lesson", "question_text",
            "option_a", "option_b", "option_c", "option_d",
            "correct_option", "sort_order",
        )
