from django.contrib import admin
from .models import Enrollment, LessonCompletion, Review, Certificate


class LessonCompletionInline(admin.TabularInline):
    model = LessonCompletion
    extra = 0


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "learning_path", "enrolled_at", "completed_at")
    list_filter = ("completed_at",)
    inlines = [LessonCompletionInline]


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "learning_path", "rating", "created_at")
    list_filter = ("rating",)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "user", "learning_path", "issued_at")
