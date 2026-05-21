import base64
import asyncio
import time
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import cv2

from detector import detect

app = FastAPI(title="AI Robotic Platform Backend API")

# Add CORS Middleware to allow connections from Vite dev environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "description": "AI Robotic Platform Backend API. Connect to /ws via WebSocket for live telemetry.",
        "model": "YOLOv8n"
    }

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("[SYSTEM] WebSocket client connected.")

    # Initialize webcam capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[WARNING] Camera 0 could not be opened. Starting in camera connection recovery loop.")

    try:
        while True:
            # Handle camera offline scenario
            if not cap.isOpened():
                await ws.send_json({
                    "frame": None,
                    "detections": [],
                    "stats": {
                        "latency": 0,
                        "mode": "Offline",
                        "model": "YOLOv8n"
                    }
                })
                # Check for camera connection again after 2 seconds
                await asyncio.sleep(2.0)
                cap = cv2.VideoCapture(0)
                continue

            start_time = time.time()

            success, raw_frame = cap.read()
            if not success:
                print("[WARNING] Failed to read frame from Camera 0. Releasing capture and waiting for reconnection...")
                cap.release()
                await asyncio.sleep(1.0)
                continue

            # Run real YOLOv8 tracking & annotation
            frame, detections = detect(raw_frame)

            # Measure processing latency in milliseconds
            latency_ms = round((time.time() - start_time) * 1000, 1)

            # Encode frame to JPEG and then to base64
            _, buffer = cv2.imencode(".jpg", frame)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")

            # Send telemetry JSON payload
            await ws.send_json({
                "frame": frame_b64,
                "detections": detections,
                "stats": {
                    "latency": latency_ms,
                    "mode": "Webcam",
                    "model": "YOLOv8n"
                }
            })

            # Small yield to cap framerate and prevent thread starvation
            await asyncio.sleep(0.01)

    except Exception as e:
        print(f"[INFO] WebSocket connection closed: {e}")
    finally:
        print("[SYSTEM] Releasing video resources and closing socket.")
        if cap is not None:
            cap.release()