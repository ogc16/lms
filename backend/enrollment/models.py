from django.db import models
from django.conf import settings


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    learning_path = models.ForeignKey(
        "learning.LearningPath",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "enrollments"
        unique_together = ("user", "learning_path")

    @property
    def total_lessons(self):
        from learning.models import Lesson
        return Lesson.objects.filter(
            module__learning_path=self.learning_path,
            status=Lesson.Status.PUBLISHED,
        ).count()

    @property
    def completed_lessons(self):
        return self.completions.count()

    @property
    def progress_percent(self):
        total = self.total_lessons
        if total == 0:
            return 0.0
        return round((self.completed_lessons / total) * 100, 1)

    @property
    def is_completed(self):
        return self.progress_percent >= 100.0

    def __str__(self):
        return f"{self.user.email} → {self.learning_path.title}"


class LessonCompletion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_completions",
    )
    lesson = models.ForeignKey(
        "learning.Lesson",
        on_delete=models.CASCADE,
        related_name="lesson_completions",
    )
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="completions"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lesson_completions"
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{self.user.email} ✓ {self.lesson.title}"
