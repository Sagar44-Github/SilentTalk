from django.contrib import admin
from .models import LetterProgress, LearningSession


@admin.register(LetterProgress)
class LetterProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "letter", "status", "guided_count", "solo_count", "last_practiced")
    list_filter = ("status", "letter")
    search_fields = ("user__username", "user__email")


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "started_at", "letters_practiced", "letters_mastered", "total_correct")
    list_filter = ("started_at",)
