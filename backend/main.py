import base64
import asyncio
import time
import threading
import concurrent.futures
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import cv2

from detector import detect, draw_cached_boxes, device

# Dedicated thread pool for CPU-heavy encoding work (separate from inference)
_encode_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="encoder")

app = FastAPI(title="AI Robotic Platform Backend API")

# Add CORS Middleware to allow connections from Vite dev environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoStream:
    """
    High-performance camera reader running on a dedicated daemon thread.
    Continuously drains the camera hardware buffer to eliminate stream delay.
    """
    def __init__(self, src=0):
        self.src = src
        self.stream = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.stream.read()
        self.started = False
        self.read_lock = threading.Lock()

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
                # Attempt camera re-acquisition periodically
                self.stream = cv2.VideoCapture(self.src)
                time.sleep(1.0)
                continue
                
            grabbed, frame = self.stream.read()
            with self.read_lock:
                self.grabbed = grabbed
                if grabbed:
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

def _encode_frame(frame):
    """
    CPU-heavy work: JPEG encode + base64. Runs in a thread pool
    to avoid blocking the asyncio event loop.
    """
    _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    return base64.b64encode(buffer).decode("utf-8")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print(f"[SYSTEM] WebSocket client connected. Engine running on: {device.upper()}")

    # Initialize and spin up the threaded background frame grabber
    vs = VideoStream(0).start()
    if not vs.isOpened():
        print("[WARNING] Threaded VideoStream failed to open Camera 0. Entering recovery loop.")

    # ── Shared state between inference producer and frame sender ──
    cached_detections = []
    last_inference_latency = 0.0
    inference_lock = threading.Lock()
    inference_running = False
    frame_counter = 0

    # Inference frequency: run YOLO every Nth frame.
    # CUDA: every frame (1). CPU: every 2nd frame to keep loop responsive.
    inference_skip_rate = 1 if device == "cuda" else 2
    print(f"[SYSTEM] Performance profiling active. Skip rate set to: {inference_skip_rate} (device: {device})")

    def run_inference(frame):
        """
        Blocking inference worker – runs in asyncio's default thread pool.
        Updates shared cached_detections via the closure.
        """
        nonlocal cached_detections, last_inference_latency, inference_running
        try:
            t0 = time.time()
            _annotated, detections = detect(frame)
            latency = round((time.time() - t0) * 1000, 1)
            with inference_lock:
                cached_detections = detections
                last_inference_latency = latency
        finally:
            with inference_lock:
                inference_running = False

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
                        "model": "YOLOv8"
                    }
                })
                await asyncio.sleep(2.0)
                continue

            success, raw_frame = vs.read()
            if not success or raw_frame is None:
                await asyncio.sleep(0.01)
                continue

            # Standardize frame resolution to 640x480 for light network payloads
            if raw_frame.shape[1] != 640 or raw_frame.shape[0] != 480:
                raw_frame = cv2.resize(raw_frame, (640, 480))

            frame_counter += 1

            # ── Launch inference asynchronously (fire-and-forget) ──
            # Only dispatch if the previous inference has finished, preventing queue pile-up.
            with inference_lock:
                should_infer = (
                    not inference_running
                    and frame_counter % inference_skip_rate == 0
                )
                if should_infer:
                    inference_running = True

            if should_infer:
                # Submit to thread pool – does NOT block the event loop
                asyncio.get_event_loop().run_in_executor(None, run_inference, raw_frame.copy())

            # ── Always draw cached boxes on the current fresh frame ──
            # This keeps the visual stream smooth at target FPS regardless of inference speed.
            annotated_frame = draw_cached_boxes(raw_frame, cached_detections)

            # Offload heavy JPEG+base64 encoding to thread pool
            frame_b64 = await asyncio.get_event_loop().run_in_executor(
                _encode_pool, _encode_frame, annotated_frame
            )

            # Read latest stats under lock
            with inference_lock:
                det_snapshot = cached_detections
                lat_snapshot = last_inference_latency

            # Send optimized telemetry JSON payload
            await ws.send_json({
                "frame": frame_b64,
                "detections": det_snapshot,
                "stats": {
                    "latency": lat_snapshot,
                    "mode": f"Webcam ({device.upper()})",
                    "model": "YOLOv8n"
                }
            })

            # Target a steady ~30 FPS stream
            loop_elapsed = time.time() - loop_start
            sleep_needed = max(0.001, 0.033 - loop_elapsed)
            await asyncio.sleep(sleep_needed)

    except Exception as e:
        print(f"[INFO] WebSocket connection closed: {e}")
    finally:
        print("[SYSTEM] Shutting down threaded grabber and releasing resources.")
        vs.release()