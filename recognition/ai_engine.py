import pickle
import mediapipe as mp
import numpy as np
import os

# ── Emotion Detection via FaceMesh ──────────────────────────────────────────
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    min_detection_confidence=0.5
)


def detect_emotion(frame_array):
    """
    Detect emotion from an RGB frame using FaceMesh landmark geometry.
    Returns one of: 'happy', 'sad', 'urgent', 'surprised', 'neutral'
    """
    results = face_mesh.process(frame_array)
    if not results.multi_face_landmarks:
        return "neutral", False  # emotion, face_detected

    landmarks = results.multi_face_landmarks[0].landmark

    # Key landmark indices
    mouth_left   = landmarks[61]    # Left mouth corner
    mouth_right  = landmarks[291]   # Right mouth corner
    mouth_top    = landmarks[13]    # Upper lip center
    mouth_bottom = landmarks[14]    # Lower lip center
    brow_left    = landmarks[70]    # Left eyebrow inner
    brow_right   = landmarks[300]   # Right eyebrow inner
    eye_top      = landmarks[159]   # Left eye top
    eye_bottom   = landmarks[145]   # Left eye bottom

    # Mouth openness (vertical distance between lips)
    mouth_open = abs(mouth_top.y - mouth_bottom.y)

    # Smile score: if mouth corners are higher than mouth center = smile
    mouth_center_y = (mouth_top.y + mouth_bottom.y) / 2
    corners_avg_y = (mouth_left.y + mouth_right.y) / 2
    smile_score = mouth_center_y - corners_avg_y

    # Eyebrow raise (surprise/urgency indicator)
    brow_avg_y = (brow_left.y + brow_right.y) / 2
    eye_avg_y = (eye_top.y + eye_bottom.y) / 2
    brow_raise = eye_avg_y - brow_avg_y

    # Eye openness
    eye_open = abs(eye_top.y - eye_bottom.y)

    # Decision logic (tuned thresholds)
    if smile_score > 0.01 and mouth_open < 0.04:
        return "happy", True
    elif brow_raise > 0.08 and eye_open > 0.025:
        return "urgent", True
    elif smile_score < -0.005:
        return "sad", True
    elif mouth_open > 0.06:
        return "surprised", True
    else:
        return "neutral", True


# ── Hand Sign Recognition ───────────────────────────────────────────────────
# Load model using absolute path so it works regardless of working directory
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.p")
model_dict = pickle.load(open(MODEL_PATH, "rb"))
model = model_dict["model"]

# MediaPipe setup — match the original main.py settings exactly
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,       # False = optimized for video frames (was True — big bug)
    min_detection_confidence=0.5,  # Match original (was 0.3)
    max_num_hands=1                # Only detect one hand (was missing)
)

# Full label mapping — model has 38 classes (A-Z + 0-9 + space + fullstop)
labels_dict = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J',
    10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S',
    19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z',
    26: '0', 27: '1', 28: '2', 29: '3', 30: '4', 31: '5', 32: '6', 33: '7', 34: '8', 35: '9',
    36: ' ',
    37: '.'
}

EXPECTED_FEATURES = 42  # 21 landmarks × 2 coordinates (x, y)


def predict_from_frame(frame_array):
    """
    Takes an RGB numpy frame, detects hand landmarks, and returns the predicted letter.
    Returns None if no hand is detected.
    """
    data_aux = []
    x_ = []
    y_ = []

    results = hands.process(frame_array)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            x_.append(x)
            y_.append(y)

        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            data_aux.append(x - min(x_))
            data_aux.append(y - min(y_))

        # Pad or truncate features to match expected size (from original main.py)
        if len(data_aux) < EXPECTED_FEATURES:
            data_aux.extend([0] * (EXPECTED_FEATURES - len(data_aux)))
        elif len(data_aux) > EXPECTED_FEATURES:
            data_aux = data_aux[:EXPECTED_FEATURES]

        prediction = model.predict([np.asarray(data_aux)])
        return labels_dict.get(int(prediction[0]), "?")

    return None