from django.contrib import admin
from .models import Enrollment, LessonCompletion


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
