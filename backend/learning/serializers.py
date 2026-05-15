from rest_framework import serializers
from .models import LearningPath, Module, Lesson, Question


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

    class Meta:
        model = LearningPath
        fields = (
            "id", "title", "description", "cover_image_url", "difficulty",
            "estimated_hours", "status", "instructor_name", "module_count",
            "lesson_count", "enrolled_count", "is_enrolled", "progress_percent",
        )

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.email

    def get_module_count(self, obj):
        return obj.modules.count()

    def get_lesson_count(self, obj):
        return Lesson.objects.filter(module__learning_path=obj).count()

    def get_enrolled_count(self, obj):
        return obj.enrollments.count()

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(user=request.user).exists()
        return False

    def get_progress_percent(self, obj):
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
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(user=request.user).exists()
        return False

    def get_progress_percent(self, obj):
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
