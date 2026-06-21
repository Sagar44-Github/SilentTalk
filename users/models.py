from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended profile for SilentTalk users."""

    ROLE_CHOICES = [
        ("learner", "Learner"),
        ("educator", "Educator"),
        ("interpreter", "Interpreter"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="learner")
    bio = models.TextField(max_length=300, blank=True, default="")
    avatar_initial = models.CharField(max_length=2, blank=True, default="")
    date_joined_display = models.DateTimeField(auto_now_add=True)

    # Stats
    total_signs_practiced = models.PositiveIntegerField(default=0)
    total_conversations = models.PositiveIntegerField(default=0)
    total_translations = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.avatar_initial and self.user:
            first = self.user.first_name[:1].upper() if self.user.first_name else ""
            last = self.user.last_name[:1].upper() if self.user.last_name else ""
            self.avatar_initial = f"{first}{last}" or self.user.username[:2].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
