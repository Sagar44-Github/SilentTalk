import cv2
import base64
import json
import numpy as np
import os
import traceback
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_engine import predict_from_frame, detect_emotion

print("[SilentTalk] AI engine loaded successfully!")

# Load the ISL word dictionary for the reverse channel
WORDS_FILE = os.path.join(os.path.dirname(__file__), "static", "recognition", "words.txt")
ISL_WORDS = set()
if os.path.exists(WORDS_FILE):
    with open(WORDS_FILE, "r") as f:
        content = f.read()
        # Parse the Python-style list from words.txt
        import re
        ISL_WORDS = set(w.strip().lower() for w in re.findall(r"'([^']+)'", content))
    print(f"[SilentTalk] Loaded {len(ISL_WORDS)} ISL words for reverse channel")

# Lazy-load gesture engine (MediaPipe model)
_gesture_engine = None


def _get_gesture_engine():
    global _gesture_engine
    if _gesture_engine is None:
        from .gesture_engine import recognize_gesture
        _gesture_engine = recognize_gesture
        print("[SilentTalk] Gesture engine loaded!")
    return _gesture_engine


def landing_page(request):
    return render(request, "recognition/landing.html")


def recognize_page(request):
    return render(request, "recognition/recognize.html")


def text_to_isl_page(request):
    return render(request, "recognition/text_to_isl.html")


def learn_isl_page(request):
    # Delegate to the learn app view for progress support
    from learn.views import learn_page
    return learn_page(request)


def login_page(request):
    # Delegate to the users app login view (handles both GET and POST)
    from users.views import login_view
    return login_view(request)


def register_page(request):
    # Delegate to the users app register view (handles both GET and POST)
    from users.views import register_view
    return register_view(request)


def gesture_page(request):
    return render(request, "recognition/gesture.html")


@csrf_exempt
def process_text(request):
    """Process text into ISL-compatible tokens.
    Words in dictionary → kept as words. Unknown words → split into letters."""
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if not text:
            return JsonResponse({"tokens": []})

        words = text.lower().split()
        tokens = []
        for word in words:
            # Remove punctuation from word
            clean = word.strip(".,!?;:'\"")
            if clean in ISL_WORDS:
                tokens.append(clean)
            else:
                # Spell out letter by letter
                for letter in clean:
                    if letter.isalnum():
                        tokens.append(letter)
        return JsonResponse({"tokens": tokens, "original": text})
    return JsonResponse({"tokens": []})


@csrf_exempt
def predict_gesture(request):
    """Single frame → MediaPipe Gesture Recognizer → gesture name + confidence."""
    if request.method == "POST":
        try:
            recognize = _get_gesture_engine()
            frame_data = request.POST.get("frame")
            if not frame_data:
                return JsonResponse({"gesture": "", "error": "No frame data"})

            img_data = base64.b64decode(frame_data.split(",")[1])
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                return JsonResponse({"gesture": "", "error": "Could not decode"})

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            name, display, confidence = recognize(frame_rgb)

            return JsonResponse({
                "gesture": name or "",
                "display": display or "",
                "confidence": round(confidence, 3),
            })
        except Exception as e:
            print(f"[SilentTalk] ERROR in predict_gesture: {e}")
            traceback.print_exc()
            return JsonResponse({"gesture": "", "error": str(e)})
    return JsonResponse({"gesture": ""})


@csrf_exempt
def predict(request):
    if request.method == "POST":
        try:
            data = request.POST.get("frame")
            if not data:
                return JsonResponse({"letter": "", "error": "No frame data received"})

            # Decode base64 image
            img_data = base64.b64decode(data.split(",")[1])
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return JsonResponse({"letter": "", "error": "Could not decode image"})

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            letter = predict_from_frame(frame_rgb)
            emotion, face_detected = detect_emotion(frame_rgb)
            return JsonResponse({
                "letter": letter or "",
                "emotion": emotion,
                "face_detected": face_detected
            })
        except Exception as e:
            print(f"[SilentTalk] ERROR in predict: {e}")
            traceback.print_exc()
            return JsonResponse({"letter": "", "error": str(e)})
    return JsonResponse({"letter": ""})

 # Tested this code one time more before committing second time😁😁 -- Found out that nothing was wrong just loading CORS error