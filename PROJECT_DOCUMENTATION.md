# SilentTalk - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Component Analysis](#component-analysis)
   - [ActionDetectionforSignLanguage](#actiondetectionforsignlanguage)
   - [AudioToSignLanguageConverter](#audiotosignlanguageconverter)
   - [Sign-Language-to-Text-and-Speech](#sign-language-to-text-and-speech)
   - [silenttalk (Django Web Application)](#silenttalk-django-application)
   - [stitch_sign_recognition (UI Components)](#stitch_sign_recognition-ui-components)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Machine Learning Models](#machine-learning-models)
7. [How to Run](#how-to-run)

---

## Project Overview

**SilentTalk** is a comprehensive accessibility platform that bridges communication between hearing and deaf/mute individuals through:
- **Sign Language Recognition** - Convert sign language gestures to text/speech
- **Text to Sign Language** - Convert text/speech to animated sign language avatars
- **Educational Tools** - Learn Indian Sign Language (ISL)

The project serves **63+ million** individuals in India who have speech/hearing impairments.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SilentTalk Architecture                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                     │
│  │  Speech Input     │         │  Sign Language   │                     │
│  │  (Microphone)     │         │  (Camera Feed)   │                     │
│  └────────┬─────────┘         └────────┬─────────┘                     │
│           │                              │                               │
│           ▼                              ▼                               │
│  ┌──────────────────┐         ┌──────────────────┐                     │
│  │  Web Speech API  │         │  MediaPipe       │                     │
│  │  (JS)            │         │  Hands           │                     │
│  └────────┬─────────┘         └────────┬─────────┘                     │
│           │                              │                               │
│           ▼                              ▼                               │
│  ┌──────────────────┐         ┌──────────────────┐                     │
│  │  Stanford Parser │         │  ML Models      │                     │
│  │  (NLP)           │         │  (TensorFlow/   │                     │
│  │                  │         │   RandomForest) │                     │
│  └────────┬─────────┘         └────────┬─────────┘                     │
│           │                              │                               │
│           ▼                              ▼                               │
│  ┌──────────────────┐         ┌──────────────────┐                     │
│  │  ISL Grammar     │         │  Text/Speech     │                     │
│  │  Translation     │         │  Output          │                     │
│  └────────┬─────────┘         └────────┬─────────┘                     │
│           │                              │                               │
│           ▼                              ▼                               │
│  ┌──────────────────┐         ┌──────────────────┐                     │
│  │  3D Avatar       │         │  GUI Display     │                     │
│  │  (JAS/CWASA)     │         │  (Tkinter/Web)   │                     │
│  └──────────────────┘         └──────────────────┘                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Analysis

### ActionDetectionforSignLanguage

**Purpose**: Real-time action/gesture recognition for sign language detection

**Key Files**:
- [`run.py`](ActionDetectionforSignLanguage/run.py) - Standalone execution file
- [`action.h5`](ActionDetectionforSignLanguage/action.h5) - Trained LSTM model (6.9 MB)
- [`Action Detection Refined.ipynb`](ActionDetectionforSignLanguage/Action%20Detection%20Refined.ipynb) - Training notebook

**How It Works**:

1. **MediaPipe Holistic Detection**
   ```python
   # Extracts 1662 features from each frame:
   # - Pose: 33 landmarks × 4 values (x, y, z, visibility) = 132
   # - Face: 468 landmarks × 3 values (x, y, z) = 1404
   # - Left Hand: 21 landmarks × 3 values = 63
   # - Right Hand: 21 landmarks × 3 values = 63
   # Total: 1662 features per frame
   ```

2. **Sequence Processing**
   - Collects 30 frames of keypoints
   - Sliding window approach
   - Real-time prediction every 30 frames

3. **LSTM Neural Network Architecture**
   ```
   Input: (30, 1662) - 30 frames, 1662 keypoint features
   │
   ├── LSTM Layer 1: 64 units, return_sequences=True, activation='relu'
   ├── LSTM Layer 2: 128 units, return_sequences=True, activation='relu'
   ├── LSTM Layer 3: 64 units, return_sequences=False, activation='relu'
   ├── Dense Layer 1: 64 units, activation='relu'
   ├── Dense Layer 2: 32 units, activation='relu'
   └── Output Layer: num_actions units, activation='softmax'
   ```

4. **Supported Actions** (Currently trained):
   - `hello`
   - `thanks`
   - `iloveyou`

**Data Collection Process**:
```
MP_Data/
├── hello/
│   ├── 0/ (30 frames: 0.npy to 29.npy)
│   ├── 1/
│   └── ... (30 sequences per action)
├── thanks/
└── iloveyou/
```

---

### AudioToSignLanguageConverter

**Purpose**: Convert spoken English text to Indian Sign Language animations

**Key Files**:
- [`server.py`](AudioToSignLanguageConverter/server.py) - Flask backend server
- [`index.html`](AudioToSignLanguageConverter/index.html) - Web interface
- [`SignFiles/`](AudioToSignLanguageConverter/SignFiles/) - 800+ SIGML animation files
- [`words.txt`](AudioToSignLanguageConverter/words.txt) - Dictionary of known ISL words

**Processing Pipeline**:

```
Speech Input (Microphone)
         │
         ▼
┌─────────────────────┐
│  Web Speech API     │  (JavaScript - client side)
│  Speech Recognition  │
└──────────┬──────────┘
           │
           ▼ (POST request)
┌─────────────────────┐
│  Flask Server       │
│  /parser endpoint   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stanford Parser    │  (NLP - parses English grammar)
│  (PCFG Model)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Tree Modification  │  (Transforms EN→ISL grammar order)
│  (NLTK)             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Lemmatization      │  (WordNetLemmatizer)
│  Stopword Removal   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Word Matching      │  (Look up SIGML files)
│  Fallback: Spell    │  (Unknown words → fingerspell)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3D Avatar Player   │  (CWASA/JAS Engine)
│  Marc Avatar        │
└─────────────────────┘
```

**ISL Grammar Transformation**:
- English: Subject + Verb + Object → ISL: Topic + Subject + Object + Verb
- Example: "I want water" → "Water I want"

**Supported Vocabulary**: 850+ verified ISL signs including:
- Common words: hello, thanks, how, what, where, name
- Letters: A-Z (fingerspelling fallback)
- Numbers: 0-100, months, time expressions

---

### Sign-Language-to-Text-and-Speech

**Purpose**: Convert ASL hand gestures to text with speech synthesis

**Key Files**:
- [`main.py`](Sign-Language-to-Text-and-Speech/main.py) - Tkinter GUI application
- [`trainClassifier.py`](Sign-Language-to-Text-and-Speech/trainClassifier.py) - Model training
- [`createDataset.py`](Sign-Language-to-Text-and-Speech/createDataset.py) - Feature extraction
- [`collectImgs.py`](Sign-Language-to-Text-and-Speech/collectImgs.py) - Image collection
- [`model.p`](Sign-Language-to-Text-and-Speech/model.p) - Trained Random Forest model

**Architecture**:

```
Camera Frame (640x480)
         │
         ▼
┌─────────────────────┐
│  MediaPipe Hands    │  (21 landmarks per hand)
│  21 × 2 = 42 features
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Normalization     │
│  (Relative coords) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Random Forest     │  (100 estimators)
│  Classifier        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Label Mapping    │
│  38 classes        │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐  ┌──────────┐
│  Text   │  │  Speech  │
│  GUI    │  │ (pyttsx3)│
└─────────┘  └──────────┘
```

**Supported Classes** (38 total):
- A-Z (26 letters)
- 0-9 (10 digits)
- Space gesture
- Full stop gesture

**Stabilization Algorithm**:
```python
stabilization_buffer = []  # Holds last 30 predictions
STABILITY_THRESHOLD = 25   # Need 25/30 same predictions
registration_delay = 1.5   # seconds between same character
```

---

### silenttalk (Django Application)

**Purpose**: Web platform integrating all SilentTalk features

**Project Structure**:
```
silenttalk/
├── manage.py
├── silenttalk/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── recognition/
│   ├── views.py          # Main logic
│   ├── ai_engine.py      # ASL letter recognition (from Sign-Language-to-Text)
│   ├── gesture_engine.py # MediaPipe gesture recognition
│   ├── model.p           # Random Forest model
│   ├── static/recognition/
│   │   ├── js/
│   │   │   ├── allcsa.js       # CWASA avatar engine
│   │   │   └── sigmlFiles.json # 850+ sign file mappings
│   │   ├── SignFiles/          # SIGML animation files
│   │   └── words.txt           # ISL dictionary
│   └── templates/recognition/
│       ├── landing.html        # Homepage
│       ├── recognize.html      # Sign → Text page
│       ├── text_to_isl.html    # Text → ISL avatar page
│       ├── gesture.html        # Word gesture mode
│       └── learn_isl.html      # Learning page
├── users/
│   ├── views.py
│   ├── urls.py
│   └── models.py
└── learn/
    ├── views.py
    └── urls.py
```

**URL Routes**:
| Route | View | Purpose |
|-------|------|---------|
| `/` | `landing_page` | Landing page |
| `/recognize/` | `recognize_page` | Sign → Text conversion |
| `/text-to-isl/` | `text_to_isl_page` | Text → ISL avatar |
| `/gesture/` | `gesture_page` | Word gesture mode (7 gestures) |
| `/learn/` | `learn_isl_page` | ISL learning section |
| `/login/` | `login_page` | User login |
| `/register/` | `register_page` | User registration |
| `/predict/` | `predict` | Letter prediction API |
| `/predict-gesture/` | `predict_gesture` | Gesture prediction API |
| `/process-text/` | `process_text` | Text → ISL tokens API |

**API Endpoints**:

```python
# POST /predict/
# Body: { frame: "data:image/jpeg;base64,..." }
# Response: { letter: "A" }

# POST /predict-gesture/
# Body: { frame: "data:image/jpeg;base64,..." }
# Response: { gesture: "thumbs_up", display: "👍", confidence: 0.95 }

# POST /process-text/
# Body: { text: "Hello how are you" }
# Response: { tokens: ["hello", "how", "are", "you"], original: "Hello how are you" }
```

**Supported Gestures** (Mode 2 - Word Gestures):
1. 👍 Thumbs Up - Good/Yes
2. 👎 Thumbs Down - Bad/No
3. ✌️ Victory - Peace
4. 🤟 I Love You - Love
5. ✊ Closed Fist - Stop/Ready
6. 🖐️ Open Palm - Hello/Stop
7. ☝️ Pointing Up - Attention

---

### stitch_sign_recognition (UI Components)

**Purpose**: Various UI/UX design iterations for SilentTalk

**Contains Multiple Design Variations**:
- `notion_dark_landing_lighter_accents/` - Dark theme landing page
- `notion_dark_login_final/` - Dark theme login page
- `polished_landing_page_with_clean_roadmap/` - Clean roadmap design
- `polished_sign_recognition/` - Sign recognition UI
- `polished_text_to_isl/` - Text to ISL UI
- `lumina_gesture/` - Gesture-focused design
- etc.

These are frontend design explorations showing the evolution of the UI.

---

## Data Flow

### Sign Language to Text Flow
```
1. User performs sign gesture
2. Camera captures frame → MediaPipe detects 21 hand landmarks
3. Landmarks normalized → 42 features extracted
4. Random Forest model predicts letter (A-Z, 0-9, space, .)
5. Stabilization buffer confirms prediction
6. Letter added to word buffer
7. Word added to sentence
8. Text-to-Speech reads sentence aloud
```

### Text to Sign Language Flow
```
1. User types text OR speaks into microphone
2. Flask backend receives text
3. Stanford Parser generates parse tree
4. Tree modified for ISL grammar (SVO → TSOV)
5. Lemmatization and stopword removal
6. Each word matched to SIGML file
7. Unknown words → fingerspelling (letter by letter)
8. CWASA avatar plays SIGML animations sequentially
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Sign Recognition** | MediaPipe, TensorFlow, LSTM |
| **Letter Recognition** | MediaPipe, Scikit-learn (RandomForest) |
| **NLP Processing** | Stanford Parser, NLTK |
| **Text-to-Speech** | pyttsx3, Web Speech API |
| **Avatar Engine** | JAS/CWASA (Java Animated Signing) |
| **Web Framework** | Django 5.x |
| **Frontend** | HTML5, CSS3, TailwindCSS, JavaScript |
| **Desktop GUI** | Tkinter |
| **Sign Files** | SiGML (Signing Gesture Markup Language) |

---

## Machine Learning Models

### Model 1: LSTM Action Recognition (action.h5)
- **Input Shape**: (30, 1662)
- **Architecture**: 3-layer LSTM
- **Training Data**: 30 videos × 3 actions × 30 frames
- **Accuracy**: ~95%+
- **Used for**: Word-level sign recognition (hello, thanks, iloveyou)

### Model 2: Random Forest Classifier (model.p)
- **Input Shape**: (42,) - 21 landmarks × 2 coordinates
- **Estimators**: 100 trees
- **Classes**: 38 (A-Z, 0-9, space, .)
- **Training Data**: 100 images × 38 classes
- **Accuracy**: ~90%+
- **Used for**: Single letter/digit recognition

### Model 3: MediaPipe Gesture Recognition (built-in)
- **Features**: 21 hand landmarks
- **Pre-trained gestures**: 7 basic gestures
- **Confidence threshold**: 0.5
- **Used for**: Quick word-level gestures

---

## How to Run

### Django Web Application (Recommended)
```bash
# 1. Navigate to project
cd "d:/Semester - 4/Full Stack Development/SilentTalk - The Project"

# 2. Activate virtual environment
cd silenttalk_env
Scripts\activate  # Windows
source bin/activate  # Linux/Mac

# 3. Install dependencies
pip install django tensorflow mediapipe scikit-learn

# 4. Run server
cd ..
python silenttalk/manage.py runserver

# 5. Open browser
# http://127.0.0.1:8000/
```

### Standalone Sign Recognition (ActionDetectionforSignLanguage)
```bash
cd ActionDetectionforSignLanguage
# Ensure action.h5 is present
python run.py
```

### Standalone Letter Recognition (Sign-Language-to-Text-and-Speech)
```bash
cd Sign-Language-to-Text-and-Speech
pip install opencv-python mediapipe scikit-learn pyttsx3 pillow
python main.py
```

### Audio to Sign Language Converter (Standalone)
```bash
cd AudioToSignLanguageConverter
pip install flask flask-cors nltk
python server.py
# Open index.html in browser (requires localhost)
```

---

## Future Enhancements

1. **Expanded Vocabulary** - More ISL words and dynamic gestures
2. **Mobile App** - React Native or Flutter deployment
3. **Real-time Translation** - Live video call integration
4. **Deep Learning** - CNN/RNN for better accuracy
5. **Multi-language Support** - Regional Indian sign languages
6. **Community Dictionary** - User-contributed signs

---

## Project Statistics

| Metric | Value |
|--------|-------|
| **Total Vocabulary** | 850+ ISL signs |
| **Supported Gestures** | 38 (A-Z, 0-9, space, .) |
| **Word Gestures** | 7 basic gestures |
| **AI Processing Latency** | ~24ms |
| **Alphabet Coverage** | A-Z (fingerspelling fallback) |
| **Sign File Count** | 800+ SIGML files |

---

## Credits

This project was developed as a comprehensive accessibility solution to bridge communication gaps for the deaf and hard-of-hearing community in India.

**Main Contributors**:
- Sign Language Recognition: MediaPipe + TensorFlow
- Audio Conversion: Stanford Parser + NLTK
- Web Platform: Django + TailwindCSS
- Avatar Engine: JAS/CWASA
