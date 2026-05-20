# Robotic Platform

A full-stack application that provides real-time video streaming and object detection capabilities. It uses a FastAPI backend equipped with YOLOv8 for computer vision tasks and a React (Vite) frontend to consume and display the real-time websocket feed.

## Features

- **Real-Time Video Streaming**: Captures video from a webcam and streams it in real-time over WebSockets using Base64 encoding.
- **Object Detection & Tracking**: Utilizes Ultralytics YOLOv8 and ByteTrack to perform object detection and tracking.
- **FastAPI Backend**: A lightweight, high-performance web server that manages WebSocket connections and computer vision processing.
- **React Frontend**: Built with Vite and React for a modern, responsive user interface.

## Directory Structure

```text
Robotic platform/
├── backend/                  # FastAPI backend server
│   ├── detector.py           # YOLOv8 object detection and tracking logic
│   ├── main.py               # FastAPI application and WebSocket endpoints
│   ├── yolov8n.pt            # Pre-trained YOLOv8 weights (downloaded on first run/included)
│   └── ...
├── frontend/                 # React frontend application
│   ├── src/                  # React source code
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies and scripts
│   ├── vite.config.js        # Vite configuration
│   └── ...
├── requirements.txt          # Python dependencies for the backend
└── .gitignore                # Git ignore rules
```

## Prerequisites

- **Python 3.8+** (for the backend)
- **Node.js 18+** (for the frontend)
- **A working webcam** (for real-time video capture)

## Installation & Setup

### 1. Backend Setup

The backend requires several Python libraries, including FastAPI, Uvicorn, OpenCV, and Ultralytics.

1. Navigate to the project root directory:
   ```bash
   cd "Robotic platform"
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
   The backend WebSocket will now be running and listening for connections at `ws://localhost:8000/ws`.

### 2. Frontend Setup

The frontend is a React application set up with Vite.

1. Navigate to the frontend directory:
   ```bash
   cd "Robotic platform/frontend"
   ```

2. Install the Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The application should now be accessible in your browser (typically at `http://localhost:5173`).

## Technologies Used

- **Backend**: Python, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [OpenCV](https://opencv.org/), [Ultralytics YOLOv8](https://docs.ultralytics.com/), WebSockets
- **Frontend**: JavaScript/TypeScript, [React](https://react.dev/), [Vite](https://vitejs.dev/)
