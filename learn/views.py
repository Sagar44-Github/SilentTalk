import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import LetterProgress, LearningSession


def learn_page(request):
    """Serve the Learn ISL page. Passes saved progress if user is logged in."""
    context = {}
    if request.user.is_authenticated:
        progress = LetterProgress.objects.filter(user=request.user)
        mastered = [p.letter for p in progress if p.status == "mastered"]
        guided = [p.letter for p in progress if p.status in ("guided", "mastered")]
        context["saved_mastered"] = json.dumps(mastered)
        context["saved_guided"] = json.dumps(guided)
        context["is_authenticated"] = True
    else:
        context["saved_mastered"] = json.dumps([])
        context["saved_guided"] = json.dumps([])
        context["is_authenticated"] = False
    return render(request, "recognition/learn_isl.html", context)


@csrf_exempt
def save_progress(request):
    """API: Save learning progress for the authenticated user.
    POST body: { mastered: ["A","B",...], guided: ["A","B","C",...] }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required", "saved": False}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    mastered_letters = set(data.get("mastered", []))
    guided_letters = set(data.get("guided", []))

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        obj, created = LetterProgress.objects.get_or_create(
            user=request.user, letter=letter
        )
        if letter in mastered_letters:
            obj.status = "mastered"
            if not obj.mastered_at:
                obj.mastered_at = timezone.now()
        elif letter in guided_letters:
            obj.status = "guided"
            obj.mastered_at = None
        else:
            obj.status = "new"
            obj.mastered_at = None
        obj.save()

    # Update user profile stats
    if hasattr(request.user, "profile"):
        request.user.profile.total_signs_practiced = len(mastered_letters) + len(guided_letters)
        request.user.profile.save(update_fields=["total_signs_practiced"])

    return JsonResponse({
        "saved": True,
        "mastered": len(mastered_letters),
        "guided": len(guided_letters),
    })


@csrf_exempt
def load_progress(request):
    """API: Load learning progress for the authenticated user."""
    if not request.user.is_authenticated:
        return JsonResponse({"mastered": [], "guided": []})

    progress = LetterProgress.objects.filter(user=request.user)
    mastered = [p.letter for p in progress if p.status == "mastered"]
    guided = [p.letter for p in progress if p.status in ("guided", "mastered")]

    return JsonResponse({"mastered": mastered, "guided": guided})
