import base64
import asyncio
import os
import time
import threading
import platform
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import cv2

from detector import detect, draw_cached_boxes, device

# Suppress noisy MSMF warnings on Windows (must be set before any VideoCapture)
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

app = FastAPI(title="AI Robotic Platform Backend API")

# Add CORS Middleware to allow connections from Vite dev environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _open_camera(src):
    """
    Open a camera with the most stable backend for the current OS.
    On Windows, DirectShow (CAP_DSHOW) is far more reliable than the
    default MSMF backend for USB webcams.
    """
    if platform.system() == "Windows":
        cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(src)

    if cap.isOpened():
        # Minimize internal buffer to 1 frame — keeps frames fresh instead of queued
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # Request 640x480 from the driver directly (avoids software resize later)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap

class VideoStream:
    """
    High-performance camera reader running on a dedicated daemon thread.
    Continuously drains the camera hardware buffer to eliminate stream delay.
    """
    def __init__(self, src=0):
        self.src = src
        self.stream = _open_camera(src)
        self.grabbed, self.frame = self.stream.read()
        self.started = False
        self.read_lock = threading.Lock()
        self._consecutive_failures = 0

    def start(self):
        if self.started:
            return self
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        while self.started:
            if not self.stream.isOpened():
                # Attempt camera re-acquisition periodically using stable backend
                print("[WARNING] Camera lost — attempting re-acquisition...")
                self.stream = _open_camera(self.src)
                time.sleep(2.0)
                continue

            grabbed, frame = self.stream.read()

            if not grabbed:
                # Back off exponentially on consecutive failures (caps at 1s)
                # This prevents flooding the terminal with grab-frame warnings
                self._consecutive_failures += 1
                backoff = min(1.0, 0.03 * (2 ** min(self._consecutive_failures, 5)))
                time.sleep(backoff)
                continue

            # Reset failure counter on success
            self._consecutive_failures = 0

            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame
            # 10ms yield to prevent CPU starvation on this background thread
            time.sleep(0.01)

    def read(self):
        with self.read_lock:
            if self.grabbed and self.frame is not None:
                return True, self.frame.copy()
            return False, None

    def isOpened(self):
        return self.stream.isOpened()

    def release(self):
        self.started = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.stream.release()

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "device": device.upper(),
        "description": "AI Robotic Platform Backend API. Connect to /ws via WebSocket for live telemetry.",
        "model": "YOLOv8n"
    }

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print(f"[SYSTEM] WebSocket client connected. Engine running on: {device.upper()}")

    # Initialize and spin up the threaded background frame grabber
    vs = VideoStream(0).start()
    if not vs.isOpened():
        print("[WARNING] Threaded VideoStream failed to open Camera 0. Entering recovery loop.")

    # Caching states
    cached_detections = []
    last_inference_latency = 0.0
    frame_counter = 0
    
    # Run YOLO inference on 1 out of every 3 frames (reduces model compute by 66%)
    # For intermediate frames, we draw cached boxes on fresh frames at 30 FPS.
    # Note: If CUDA/GPU is available, you can lower this to 1 (infer every single frame) for maximum accuracy!
    inference_skip_rate = 1 if device == "cuda" else 3
    print(f"[SYSTEM] Performance profiling active. Skip rate set to: {inference_skip_rate} (device: {device})")

    try:
        while True:
            loop_start = time.time()

            # Handle camera offline / recovery state
            if not vs.isOpened():
                await ws.send_json({
                    "frame": None,
                    "detections": [],
                    "stats": {
                        "latency": 0,
                        "mode": "Offline",
                        "model": "YOLOv8n"
                    }
                })
                # Check for camera availability every 2 seconds
                await asyncio.sleep(2.0)
                continue

            success, raw_frame = vs.read()
            if not success or raw_frame is None:
                # Wait 10ms for grabber thread to write a valid frame
                await asyncio.sleep(0.01)
                continue

            # Standardize frame resolution to 640x480 for light network payloads
            if raw_frame.shape[1] != 640 or raw_frame.shape[0] != 480:
                raw_frame = cv2.resize(raw_frame, (640, 480))

            frame_counter += 1

            # Decide whether to execute active inference or render from cache
            if frame_counter % inference_skip_rate == 0:
                start_time = time.time()
                # Offload heavy model inference to background thread pool (prevents event loop blocking)
                annotated_frame, detections = await asyncio.to_thread(detect, raw_frame)
                last_inference_latency = round((time.time() - start_time) * 1000, 1)
                cached_detections = detections
            else:
                # Interpolate cached bounding boxes onto fresh frame (extremely fast, < 0.1ms)
                annotated_frame = draw_cached_boxes(raw_frame, cached_detections)

            # JPEG compress (quality 75) to keep base64 packet sizes down by ~60%
            _, buffer = cv2.imencode(".jpg", annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            frame_b64 = base64.b64encode(buffer).decode("utf-8")

            # Send optimized telemetry JSON payload
            await ws.send_json({
                "frame": frame_b64,
                "detections": cached_detections,
                "stats": {
                    "latency": last_inference_latency,
                    "mode": f"Webcam ({device.upper()})",
                    "model": "YOLOv8n"
                }
            })

            # Calculate processing duration and sleep precisely to target a steady 30 FPS stream
            loop_elapsed = time.time() - loop_start
            sleep_needed = max(0.001, 0.033 - loop_elapsed)  # 0.033s = ~30 FPS
            await asyncio.sleep(sleep_needed)

    except Exception as e:
        print(f"[INFO] WebSocket connection closed: {e}")
    finally:
        print("[SYSTEM] Shutting down threaded grabber and releasing resources.")
        vs.release()