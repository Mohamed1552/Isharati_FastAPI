# Isharati FastAPI — Arabic Sign Language Translator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-orange)
![Computer Vision](https://img.shields.io/badge/Computer%20Vision-Pose%20Estimation-purple)
![NLP](https://img.shields.io/badge/NLP-Arabic%20Refinement-red)

**Isharati** is a FastAPI backend for two-way Arabic/Egyptian sign language translation.  
It supports Arabic text or speech input and converts it into sign pose animation files, and it also supports sign-video input and predicts Arabic words or short sentences.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Main Features](#main-features)
- [System Pipeline](#system-pipeline)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Run Locally](#run-locally)
- [API Endpoints](#api-endpoints)
- [Model Files](#model-files)
- [Deployment Notes](#deployment-notes)
- [Troubleshooting](#troubleshooting)
- [Future Work](#future-work)

---

## Project Overview

The backend combines:

- **Computer Vision** for sign-video preprocessing and pose/keypoint extraction.
- **Deep Learning** for sign recognition from processed pose features.
- **Arabic NLP** for converting raw predicted glosses into more natural Egyptian Arabic sentences.
- **Pose retrieval and smoothing** for generating sign-language motion from Arabic text or speech.
- **Cloudinary integration** for storing generated `.pose` files and serving them to the frontend.

This API is designed to be used with a web frontend where users can:

1. Enter Arabic text and receive a sign animation.
2. Upload Arabic speech and receive a sign animation.
3. Upload a sign-language video and receive Arabic text.
4. Upload a full sentence video and receive a cleaned Arabic sentence.

---

## Main Features

### Text / Speech to Sign

- Arabic sentence input.
- Egyptian Arabic speech recognition.
- Arabic text normalization and tokenization.
- Dataset token matching with exact, safe fuzzy, and character-level fallback.
- Pose retrieval from stored `.pose` URLs.
- Pose concatenation and smoothing.
- Upload generated `.pose` file to Cloudinary.
- Generate browser-compatible H.264 MP4 video from pose files.

### Sign to Text

- Upload one or more sign videos.
- Preprocess videos into model-ready pose features.
- Predict sign words using a trained deep learning model.
- Return raw predicted words.
- Optional NLP refinement to generate a natural Egyptian Arabic sentence.

### Full Sentence Video Mode

- Upload one continuous sign-language video.
- Split the video into time windows.
- Predict each window.
- Reduce repeated words from overlapping segments.
- Return a final Arabic sentence.

---

## System Pipeline

### Text / Speech to Sign

```text
Arabic Text / Speech
        ↓
Speech Recognition / Text Input
        ↓
Arabic Normalization + Tokenization
        ↓
Pose Retrieval from poses.json
        ↓
Pose Stitching + Smoothing
        ↓
Upload .pose to Cloudinary
        ↓
Generate / Stream MP4 Animation
```

### Sign to Text

```text
Sign Video
   ↓
Video Preprocessing
   ↓
Pose / Keypoint Feature Extraction
   ↓
Deep Learning Sign Recognition Model
   ↓
Raw Words
   ↓
Optional NLP Refinement
   ↓
Arabic Sentence Output
```

---

## Project Structure

```text
Text_to_sign_FastApI-main/
├── api/
│   └── routes/
│       ├── text_to_sign.py              # Text → pose file
│       ├── Speech_to_text.py            # Speech → text → pose file
│       ├── video.py                     # Pose file → MP4 video stream
│       ├── sign_to_text.py              # Word-level sign recognition
│       └── full_sentence_video.py       # Full sentence video recognition
│
├── configs/
│   └── cloudinary_config.py             # Cloudinary setup
│
├── models/
│   ├── aux_10A_mean.npy
│   ├── aux_10A_std.npy
│   └── aux_10A_names.json
│
├── schemas/
│   └── requests.py                      # Pydantic request schemas
│
├── services/
│   ├── arabic_normalizer.py             # Arabic token mapping
│   ├── pose_retriever.py                # Download pose files
│   ├── pose_smoother.py                 # Concatenate pose files
│   ├── animation_generator.py           # Generate H.264 MP4 animation
│   ├── speech_to_text.py                # Arabic speech recognition
│   ├── video_processor.py               # Video preprocessing
│   ├── sign_predictor.py                # Model inference
│   ├── model_architecture.py            # Deep learning model architecture
│   ├── full_sentence_video_service.py   # Sliding-window sentence recognition
│   └── nlp_refiner.py                   # Egyptian Arabic NLP refinement
│
├── config.py                            # Global paths and model settings
├── main.py                              # FastAPI application entry point
├── poses.json                           # Sign token → pose URL mapping
├── requirements.txt                     # Python dependencies
└── README.md
```

---

## Requirements

- Python **3.10+** recommended.
- FFmpeg support through `imageio-ffmpeg`.
- Cloudinary account for generated pose file storage.
- OpenRouter API key for optional Arabic NLP refinement.
- Trained sign-recognition model files inside the `models/` directory.

GPU is recommended for sign-video inference. The API can run on CPU, but video processing and model inference may be slow.

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Cloudinary
CLOUD_NAME=your_cloudinary_cloud_name
CLOUD_API_KEY=your_cloudinary_api_key
CLOUD_API_SECRET=your_cloudinary_api_secret

# Optional NLP refinement
OPENROUTER_API_KEY=your_openrouter_api_key
NLP_MODEL_NAME=openai/gpt-4o-mini
OPENROUTER_REFERER=https://your-app-url.com
OPENROUTER_TITLE=Isharati
```

Never commit the real `.env` file to GitHub.

---

## Installation

```bash
# 1) Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

# 2) Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3) Upgrade pip
python -m pip install --upgrade pip

# 4) Install dependencies
pip install -r requirements.txt
```

---

## Run Locally

```bash
uvicorn main:app --reload
```

The API will start at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### 1. Text to Sign

Converts Arabic text into a generated `.pose` file URL.

```http
POST /text-to-sign
Content-Type: application/json
```

Request body:

```json
{
  "sentence": "انا بحب مصر",
  "request_id": "optional-custom-id"
}
```

Example response:

```json
{
  "success": true,
  "request_id": "optional-custom-id",
  "pose_URL": "https://res.cloudinary.com/.../generated_pose/optional-custom-id.pose",
  "tokens": ["انا", "يحب", "مصر"]
}
```

---

### 2. Speech to Sign

Uploads an audio file, transcribes Arabic speech, and converts the result into a `.pose` file.

```http
POST /speech-to-text
Content-Type: multipart/form-data
```

Form data:

| Field | Type | Required | Description |
|---|---|---:|---|
| `audio` | file | Yes | Audio file such as WAV, MP3, M4A |
| `request_id` | string | No | Optional custom ID |

Example response:

```json
{
  "success": true,
  "request_id": "abc123",
  "pose_URL": "https://res.cloudinary.com/.../generated_pose/abc123.pose",
  "sentence": "انا بحب مصر",
  "tokens": ["انا", "يحب", "مصر"]
}
```

---

### 3. Generate Video from Pose

Streams a browser-compatible MP4 video for a generated pose request.

```http
GET /video/{request_id}
```

Example:

```text
GET /video/abc123
```

The response is streamed as:

```text
video/mp4
```

---

### 4. Sign to Text

Uploads one or more sign videos or `.npz` files and returns predicted Arabic words.

```http
POST /sign-to-text
Content-Type: multipart/form-data
```

Form data:

| Field | Type | Required | Description |
|---|---|---:|---|
| `files` | file[] | Yes | One or more video / `.npz` files |
| `use_nlp` | bool | No | Default `true`; refines raw words into Arabic sentence |
| `req_id` | string | No | Optional request ID |

Example response:

```json
{
  "req_id": "generated-id",
  "status": "success",
  "raw_words": ["انا", "مدرسة"],
  "raw_sentence": "انا - مدرسة",
  "final_sentence": "أنا رايح المدرسة."
}
```

---

### 5. Full Sentence Video Recognition

Uploads one continuous sign-language video and returns the predicted sentence.

```http
POST /sign-to-text/full-sentence-video
Content-Type: multipart/form-data
```

Form data:

| Field | Type | Default | Description |
|---|---|---:|---|
| `file` | file | Required | Full sign-language video |
| `use_nlp` | bool | `true` | Refine predicted words into Egyptian Arabic |
| `window_seconds` | float | `3.0` | Length of each analysis window |
| `stride_seconds` | float | `2.5` | Step between windows |
| `min_confidence` | float | `0.30` | Minimum confidence for accepted words |
| `min_margin` | float | `0.08` | Minimum top1-top2 margin |
| `min_time_gap` | float | `4.0` | Duplicate-word suppression time |
| `max_segments` | int | `10` | Maximum windows to process |
| `debug` | bool | `false` | Return extra prediction details |

Example response:

```json
{
  "status": "success",
  "mode": "full_sentence_video_word_level_v2",
  "req_id": "generated-id",
  "filename": "sentence.mp4",
  "raw_words": ["انا", "شغل", "بكرة"],
  "raw_sentence": "انا - شغل - بكرة",
  "final_sentence": "أنا هروح الشغل بكرة."
}
```

---

## Model Files

The sign-recognition service expects model files in the `models/` folder.

Common expected files:

```text
models/
├── best_model.pt or best_model.pth
├── label_map.csv or label_map_used.csv
├── training_config.json
├── aux_10A_mean.npy
├── aux_10A_std.npy
└── aux_10A_names.json
```

Large model files should not be committed directly to GitHub if they exceed GitHub limits. Use one of these options instead:

- Git LFS.
- Cloud storage download script.
- Release assets.
- Private deployment storage.

---

## Deployment Notes

For production deployment:

- Use environment variables instead of hardcoded secrets.
- Keep `.env` out of GitHub.
- Use HTTPS for camera access in the frontend.
- Run the API behind a reverse proxy or managed cloud service.
- Increase request timeout for video inference endpoints.
- Prefer GPU hosting for sign-video recognition.
- Store generated media in Cloudinary or another object storage service.

Example production command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Troubleshooting

### `OPENROUTER_API_KEY not found`

The NLP refinement will be disabled or fail if the key is missing. Add it to `.env` or set `use_nlp=false` when testing sign-to-text endpoints.

### Cloudinary upload fails

Check these variables:

```env
CLOUD_NAME=
CLOUD_API_KEY=
CLOUD_API_SECRET=
```

Also make sure the Cloudinary account allows raw file uploads.

### Video generated but browser shows 0 seconds

The animation generator converts the output to H.264 MP4 using `imageio-ffmpeg`. Make sure `imageio-ffmpeg` is installed and the server has permission to create temporary files.

### Sign-to-text is slow

CPU inference can be slow. Use CUDA/GPU where possible and reduce `max_segments` for full-sentence videos.

---

## Future Work

- Add a 3D avatar instead of skeleton visualization.
- Extend the supported Arabic/Egyptian Sign Language vocabulary.
- Improve full sentence recognition using motion-based segmentation.
- Add real-time motion trigger to avoid predicting while the user is not signing.
- Improve frontend playback using a dedicated pose/animation viewer.
- Add API authentication using an `x-api-key` header.
- Add Docker support for easier deployment.

---

## Team / Credits

This backend was developed as part of the **Isharati** graduation project, combining computer vision, deep learning, Arabic NLP, and cloud deployment to make Arabic sign-language translation more accessible.
