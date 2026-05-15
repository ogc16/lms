from rest_framework import serializers
from .models import Enrollment, LessonCompletion


class EnrollmentSerializer(serializers.ModelSerializer):
    path_title = serializers.CharField(source="learning_path.title", read_only=True)
    progress_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            "id", "user", "learning_path", "path_title",
            "enrolled_at", "completed_at", "progress_percent",
        )
        read_only_fields = ("id", "user", "enrolled_at", "completed_at", "progress_percent")


class LessonCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCompletion
        fields = ("id", "user", "lesson", "enrollment", "completed_at")
        read_only_fields = ("id", "user", "completed_at")
