# Robotic Platform

A Python-based AI application that provides real-time video streaming, object detection, facial recognition, and speech recognition capabilities.

## Features

- **Object Detection**: Utilizes Ultralytics YOLOv8s-World and ByteTrack to perform open-vocabulary object detection and tracking.
- **Face Recognition**: Includes a vision runtime (`vision_runtime.py`) that tracks individuals, allows for real-time face enrollment, and recognizes known people with TTS greetings.
- **Speech Recognition**: Includes a dedicated module (`speech_recognition/speech_runtime.py`) for Voice Activity Detection (VAD) and speaker diarization/identification to recognize known speakers and cluster unknown speakers.

## Directory Structure

```text
Robotic-platform/
├── backend/                  # Core Python modules
│   ├── detector.py           # YOLOv8s-World object detection and tracking logic
│   ├── vision_runtime.py     # Standalone runtime for face recognition & enrollment
│   ├── face/                 # Face recognition and enrollment modules
│   ├── speech_recognition/   # Speaker recognition and diarization modules
│   ├── yolov8s-world.pt      # Pre-trained YOLOv8s-World weights
│   └── ...
├── requirements.txt          # Python dependencies
├── architecture_walkthrough.md # Detailed architecture and data flow documentation
└── README.md
```

## Prerequisites

- **Python 3.8+**
- **A working webcam/IP Camera** (for real-time video capture and face recognition)
- **A working microphone** (for speech recognition features)

## Installation & Setup

1. Navigate to the project root directory:
   ```bash
   cd "Robotic-platform"
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Vision Runtime (Face Recognition & Enrollment)
To run the standalone vision runtime with facial recognition:
```bash
cd backend
python vision_runtime.py
```
- Press **`N`** to enroll a new person in the database.
- Press **`Q`** to quit.

### 2. Speech Recognition Scanner
To run the speech recognition room scanner:
```bash
cd backend/speech_recognition
python speech_runtime.py 5
```
*(The argument `5` is the scan duration in seconds).*

## Technologies Used

- **Computer Vision**: [OpenCV](https://opencv.org/), [Ultralytics YOLOv8s-World](https://docs.ultralytics.com/)
- **Audio & Speech**: Python audio libraries for VAD and embedding extraction.
