import numpy as np
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Path to the MediaPipe Gesture Recognizer model
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "static", "recognition", "gesture_recognizer.task"
)

print(f"[SilentTalk] Loading MediaPipe Gesture Recognizer from: {MODEL_PATH}")

# Read model as bytes to avoid MediaPipe's path resolution issues on Windows
with open(MODEL_PATH, "rb") as f:
    model_data = f.read()

# Create gesture recognizer using buffer (avoids path bug)
base_options = python.BaseOptions(model_asset_buffer=model_data)
options = vision.GestureRecognizerOptions(
    base_options=base_options,
    num_hands=2,
)
recognizer = vision.GestureRecognizer.create_from_options(options)

# Friendly display names for gestures
GESTURE_NAMES = {
    "None": "",
    "Closed_Fist": "Fist ✊",
    "Open_Palm": "Open Palm 🖐️",
    "Pointing_Up": "Point Up ☝️",
    "Thumb_Down": "Thumbs Down 👎",
    "Thumb_Up": "Thumbs Up 👍",
    "Victory": "Victory ✌️",
    "ILoveYou": "I Love You 🤟",
}

print(f"[SilentTalk] Gesture Recognizer ready! Supports {len(GESTURE_NAMES)-1} gestures")


def recognize_gesture(frame_rgb):
    """Recognize hand gesture from an RGB frame.
    Returns (gesture_name, display_name, confidence) or (None, None, 0).
    """
    # Convert numpy array to MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    # Run recognition
    result = recognizer.recognize(mp_image)

    if result.gestures and len(result.gestures) > 0:
        top_gesture = result.gestures[0][0]
        name = top_gesture.category_name
        confidence = top_gesture.score
        display = GESTURE_NAMES.get(name, name)
        return name, display, float(confidence)

    return None, None, 0.0
