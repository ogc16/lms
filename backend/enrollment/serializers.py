from rest_framework import serializers
from .models import Enrollment, Review, Certificate


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


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "user", "learning_path", "rating", "comment", "created_at")
        read_only_fields = ("id", "user", "created_at")


class CertificateSerializer(serializers.ModelSerializer):
    path_title = serializers.CharField(source="learning_path.title", read_only=True)

    class Meta:
        model = Certificate
        fields = ("id", "user", "learning_path", "path_title", "certificate_id", "issued_at")
        read_only_fields = ("id", "user", "certificate_id", "issued_at")
