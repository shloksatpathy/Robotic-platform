# pyrefly: ignore [missing-import]
import cv2
import numpy as np
import torch
from ultralytics import YOLO

# Detect best available hardware device (GPU CUDA vs CPU fallback)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[SYSTEM] Initializing YOLOv8n engine on device: {device.upper()}")

import os

import os

try:
    if os.path.exists("yolov8s-world.engine"):
        model_path = "yolov8s-world.engine"
    elif os.path.exists("yolov8s-world.onnx"):
        model_path = "yolov8s-world.onnx"
    else:
        model_path = "yolov8s-world.pt"
        
    model = YOLO(model_path)

    model.set_classes([
    # Human related (merged: head→face, arm→hand)
    "person",
    "hand",
    "face",

    # Computers & electronics (merged: earphones→headphones)
    "laptop",
    "computer monitor",
    "keyboard",
    "mouse",
    "cell phone",
    "printer",
    "scanner",
    "microphone",
    "speaker",
    "headphones",
    "router",
    "circuit board",
    "battery",
    "charger",
    "charging cable",
    "usb drive",

    # Furniture (merged: table→desk)
    "chair",
    "couch",
    "desk",
    "cabinet",
    "drawer",
    "bookshelf",

    # Stationery (merged: pencil/marker→pen, paper→document)
    "pen",
    "notebook",
    "book",
    "document",
    "folder",
    "calendar",
    "sticky note",

    # Personal items (merged: wallet→card)
    "backpack",
    "handbag",
    "suitcase",
    "glasses",
    "watch",
    "keys",
    "card",

    # Desk items
    "bottle",
    "cup",
    "plate",
    "bowl",
    "scissors",
    "tissue box",

    # Office infrastructure
    "stairs",
    "fire extinguisher",
    "clock",
    "potted plant",

    # Robotics / engineering
    "toolbox",
    "screwdriver",
    "multimeter",
    "sensor",
    "motor",
    "drone",
    "robot",
    "camera"
])
    if model is not None:
        model.to(device)
except Exception as e:
    print(f"Error loading YOLO model on device {device}: {e}")
    model = None

# ── Confusable class pairs that need crop-level resolution ──
# Maps each confusable class to a list of classes it gets confused with
CONFUSABLE_GROUPS = {
    "cell phone": "card",
    "card": "card",       # always re-verify card detections
    "book": "card",       # CLIP confuses card/book (both flat rectangles)
}

def resolve_class_confusion(frame, class_name, coords):
    """
    Signals used:
      1. Laplacian variance — measures texture sharpness (printed text >> screen content)
      2. Canny edge density — printed borders and text create dense edges
      3. Grayscale std dev — printed content creates varied intensity patterns
      4. Bounding box area — cards are physically smaller than books
    """
    if class_name not in CONFUSABLE_GROUPS:
        return class_name

    x1, y1, x2, y2 = [int(c) for c in coords]
    h_frame, w_frame = frame.shape[:2]

    # Clamp to frame boundaries
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w_frame, x2), min(h_frame, y2)

    if x2 - x1 < 10 or y2 - y1 < 10:
        return class_name  # Crop too small to analyze

    crop = frame[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # 1. Laplacian variance — measures texture/sharpness
    #    Printed text and logos: high variance (sharp edges at many scales)
    #    Phone screen (off=dark, on=smooth UI): lower variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 2. Edge density — Canny edges as fraction of total pixels
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.count_nonzero(edges) / max(edges.size, 1)

    # 3. Grayscale std dev — printed content creates varied intensity
    gray_std = float(gray.std())

    # 4. Bounding box area as fraction of the full frame
    box_area = (x2 - x1) * (y2 - y1)
    frame_area = h_frame * w_frame
    area_ratio = box_area / max(frame_area, 1)

    # Score: positive = card-like, negative = phone/book-like
    score = 0.0

    # Printed text/logos create high Laplacian variance (strongest signal)
    if laplacian_var > 500:
        score += 1.5  # Strong card signal
    elif laplacian_var < 150:
        score -= 1.5  # Smooth screen = phone

    # ID cards have dense edges from text, borders, printed elements
    if edge_density > 0.08:
        score += 1.0
    elif edge_density < 0.04:
        score -= 1.0

    # Printed content creates high grayscale variance
    if gray_std > 55:
        score += 0.5
    elif gray_std < 25:
        score -= 0.5

    # ID cards are small — typically <5% of frame area
    if area_ratio < 0.05:
        score += 0.5
    elif area_ratio > 0.12:
        score -= 0.5

    # Resolve: need strong agreement to reclassify
    if score >= 2.0:
        return "card"
    elif score <= -2.0:
        # Large + smooth = likely a book; otherwise phone
        if area_ratio > 0.08:
            return "book"
        return "cell phone"

    # Not confident enough to override — keep YOLO's original label
    return class_name

# Dynamic color map for drawing cached boxes
CLASS_COLORS = {
    "person": (255, 180, 0),      # Cyber Cyan/Blue BGR
    "card": (0, 255, 120),         # Neon Green BGR
    "cell phone": (0, 200, 255),   # Orange BGR
    "cup": (192, 132, 252),        # Glowing Purple BGR
}

def draw_cached_boxes(frame, detections):
    """
    Renders cached bounding boxes and labels onto a raw frame using OpenCV.
    Matches YOLO's native visual styling closely to ensure fluid visual transitions.
    """
    annotated = frame.copy()
    
    for item in detections:
        box = item.get("box")
        if not box or len(box) != 4:
            continue
            
        x1, y1, x2, y2 = box
        cls_name = item.get("class", "object")
        conf = item.get("confidence", 0.0)
        track_id = item.get("id")
        
        # Determine outline color (fallback to neon cyan if class not mapped)
        color = CLASS_COLORS.get(cls_name, (255, 229, 0))
        
        # 1. Draw outer bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Create label string: e.g. "person #1 0.94" or "person 0.94"
        label = f"{cls_name}"
        if track_id is not None:
            label += f" #{track_id}"
        label += f" {conf:.2f}"
        
        # Get text sizing to size the solid label tab background
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 1
        text_size, baseline = cv2.getTextSize(label, font, font_scale, thickness)
        text_w, text_h = text_size
        
        # 2. Draw solid label tag container just above box
        tab_y1 = max(0, y1 - text_h - 8)
        tab_y2 = y1
        cv2.rectangle(annotated, (x1, tab_y1), (x1 + text_w + 10, tab_y2), color, -1)
        
        # 3. Draw text in black on top of the solid tab
        cv2.putText(
            annotated, 
            label, 
            (x1 + 5, y1 - 4), 
            font, 
            font_scale, 
            (0, 0, 0),  # Black text BGR
            thickness, 
            cv2.LINE_AA
        )
        
    return annotated


def detect(frame):
    """
    Runs YOLOv8 object tracking on the input frame with hardware acceleration.
    Returns:
        annotated_frame (numpy.ndarray): Frame plotted with active tracking boxes.
        detections (list): List of detected objects with class, confidence, and box coordinates.
    """
    if model is None:
        return frame, []

    try:
        # Run tracking using ByteTrack, utilizing selected hardware device
        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            device=device,
            verbose=False,
            conf=0.15
        )
    except Exception as e:
        # Fallback to standard inference if tracker fails or is not found
        try:
            results = model(frame, device=device, verbose=False)
        except Exception as ex:
            print(f"Error during YOLO detection: {ex}")
            return frame, []

    detections = []
    annotated_frame = frame.copy()

    if results and len(results) > 0:
        result = results[0]

        # Extract details including raw box coordinates for interpolation/caching
        if result.boxes is not None:
            for box in result.boxes:
                if box.cls is not None and len(box.cls) > 0:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0]) if box.conf is not None else 0.0
                    class_name = model.names[cls]
                    
                    # Grab coordinates [x1, y1, x2, y2]
                    coords = box.xyxy[0].tolist() if box.xyxy is not None else [0, 0, 0, 0]

                    # Resolve known CLIP confusion pairs via crop analysis
                    class_name = resolve_class_confusion(frame, class_name, coords)

                    # Get tracking ID if available
                    track_id = int(box.id[0].item()) if box.id is not None else None
                    
                    detections.append({
                        "id": track_id,
                        "class": class_name,
                        "confidence": round(conf, 2),
                        "box": [int(c) for c in coords]
                    })

    # Draw boxes AFTER resolver has corrected class names
    # (replaces result.plot() which drew uncorrected YOLO labels)
    annotated_frame = draw_cached_boxes(frame, detections)

    return annotated_frame, detections