from django.db import models
from django.conf import settings


class LearningPath(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        ARCHIVED = "ARCHIVED", "Archived"

    class Difficulty(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image_url = models.URLField(max_length=512, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    difficulty = models.CharField(max_length=16, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    estimated_hours = models.IntegerField(default=0)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_paths",
        limit_choices_to={"role": "INSTRUCTOR"},
    )
    prerequisites = models.ManyToManyField(
        "self",
        through="PathPrerequisite",
        symmetrical=False,
        related_name="dependent_paths",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_paths"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PathPrerequisite(models.Model):
    path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE, related_name="prereq_links"
    )
    prerequisite = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE, related_name="required_by_links"
    )

    class Meta:
        db_table = "path_prerequisites"
        unique_together = ("path", "prerequisite")


class Module(models.Model):
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE, related_name="modules"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "modules"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.learning_path.title} → {self.title}"


class Lesson(models.Model):
    class ContentType(models.TextChoices):
        VIDEO = "VIDEO", "Video"
        MARKDOWN = "MARKDOWN", "Markdown"
        QUIZ = "QUIZ", "Quiz"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"

    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=16, choices=ContentType.choices)
    content_url = models.URLField(max_length=512, blank=True)
    content_body = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    sort_order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lessons"
        ordering = ["sort_order"]

    def __str__(self):
        return self.title


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1,
        choices=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
    )
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "questions"
        ordering = ["sort_order"]

    def __str__(self):
        return self.question_text[:80]
