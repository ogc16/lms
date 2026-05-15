from django.contrib import admin
from .models import LearningPath, PathPrerequisite, Module, Lesson, Question


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "status", "difficulty", "created_at")
    list_filter = ("status", "difficulty")
    search_fields = ("title", "instructor__email")
    inlines = [ModuleInline]


@admin.register(PathPrerequisite)
class PathPrerequisiteAdmin(admin.ModelAdmin):
    list_display = ("path", "prerequisite")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "learning_path", "sort_order")
    inlines = [LessonInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "content_type", "status", "sort_order")
    list_filter = ("content_type", "status")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "lesson", "correct_option", "sort_order")
    list_filter = ("lesson__module__learning_path",)
