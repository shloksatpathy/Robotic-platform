from fastapi import FastAPI, WebSocket
import cv2

from detector import detect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        if not ret:
            continue

        _, buffer = cv2.imencode(".jpg", frame)

        frame_b64 = base64.b64encode(buffer).decode("utf-8")

        await ws.send_json({
            "frame": frame_b64
        })
        
"""@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    cap = cv2.VideoCapture(0)

    while True:

        success, frame = cap.read()

        if not success:
            continue

        detections = detect(frame)

        await ws.send_json({
            "detections": detections
        })"""



# code for the static constant data to the frontend ment for testing of the frontend 
"""
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    while True:

        await ws.send_json({
            "detections": [
                {
                    "class": "person",
                    "confidence": 0.95
                },
                {
                    "class": "bottle",
                    "confidence": 0.88
                }
            ]
        })

        await asyncio.sleep(1)"""