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

    _total_lessons_cache = None
    _completed_lessons_cache = None

    @property
    def total_lessons(self):
        if self._total_lessons_cache is not None:
            return self._total_lessons_cache
        from learning.models import Lesson
        self._total_lessons_cache = Lesson.objects.filter(
            module__learning_path=self.learning_path,
            status=Lesson.Status.PUBLISHED,
        ).count()
        return self._total_lessons_cache

    @property
    def completed_lessons(self):
        if self._completed_lessons_cache is not None:
            return self._completed_lessons_cache
        self._completed_lessons_cache = self.completions.count()
        return self._completed_lessons_cache

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


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    learning_path = models.ForeignKey(
        "learning.LearningPath",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.IntegerField(choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        unique_together = ("user", "learning_path")

    def __str__(self):
        return f"{self.user.email} → {self.learning_path.title} ({self.rating}★)"


class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    learning_path = models.ForeignKey(
        "learning.LearningPath",
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    certificate_id = models.CharField(max_length=64, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "certificates"
        unique_together = ("user", "learning_path")

    def __str__(self):
        return f"{self.certificate_id} — {self.user.email} ✓ {self.learning_path.title}"
