from django.db import models
from django.contrib.auth.models import User


class LetterProgress(models.Model):
    """Tracks per-letter learning progress for each user."""

    STATUS_CHOICES = [
        ("new", "New"),
        ("guided", "Guided Complete"),
        ("mastered", "Mastered"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="letter_progress")
    letter = models.CharField(max_length=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new")
    guided_count = models.PositiveIntegerField(default=0)
    solo_count = models.PositiveIntegerField(default=0)
    total_attempts = models.PositiveIntegerField(default=0)
    last_practiced = models.DateTimeField(auto_now=True)
    mastered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "letter")
        ordering = ["letter"]

    def __str__(self):
        return f"{self.user.username} — {self.letter} ({self.get_status_display()})"


class LearningSession(models.Model):
    """Records each learning session for analytics."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learning_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    letters_practiced = models.PositiveIntegerField(default=0)
    letters_mastered = models.PositiveIntegerField(default=0)
    total_correct = models.PositiveIntegerField(default=0)
    total_attempts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Session {self.id} — {self.user.username} ({self.started_at:%Y-%m-%d %H:%M})"
