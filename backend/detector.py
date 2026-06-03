# pyrefly: ignore [missing-import]
import tensorrt
import cv2
import numpy as np
import torch
from ultralytics import YOLO

# Detect best available hardware device (GPU CUDA vs CPU fallback)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[SYSTEM] Initializing YOLOv8n engine on device: {device.upper()}")

import os

# Define the custom classes that YOLO-World should look for
custom_classes = [ "person", "hand", "face", "laptop", "computer monitor", "keyboard", "mouse", 
            "cell phone", "printer", "scanner", "microphone", "speaker", "headphones", 
            "router", "circuit board", "battery", "charger", "charging cable", "usb drive",
            "chair", "couch", "desk", "cabinet", "drawer", "bookshelf", "pen", "notebook", 
            "book", "document", "folder", "calendar", "sticky note", "backpack", "handbag", 
            "suitcase", "glasses", "watch", "keys", "card", "bottle", "cup", "plate", 
            "bowl", "scissors", "tissue box", "stairs", "fire extinguisher", "clock", 
            "potted plant", "toolbox", "screwdriver", "multimeter", "sensor", "motor", 
            "drone", "robot", "camera"]

try:
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    engine_path = os.path.join(backend_dir, "yolov8s-world.engine")
    onnx_path = os.path.join(backend_dir, "yolov8s-world.onnx")
    pt_path = os.path.join(backend_dir, "yolov8s-world.pt")

    if os.path.exists(engine_path):
        model_path = engine_path
        print(f"[SYSTEM] Loading optimized TensorRT engine: {model_path}")
    elif os.path.exists(onnx_path):
        model_path = onnx_path
        print(f"[SYSTEM] Loading ONNX model: {model_path}")
    else:
        model_path = pt_path
        print(f"[SYSTEM] Loading PyTorch weights: {model_path}")
        
    # Explicitly define task='detect' to avoid warnings when loading .engine/.onnx
    model = YOLO(model_path, task='detect')

    # Only .pt models support dynamic class setting via set_classes
    if model_path.endswith('.pt') and hasattr(model, 'set_classes'):
        model.set_classes(custom_classes)
    if model is not None and model_path.endswith('.pt'):
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

    # 5. Aspect ratio
    w = x2 - x1
    h = y2 - y1
    aspect_ratio = max(w, h) / max(min(w, h), 1)

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

    # Cards have a standard aspect ratio (~1.58). Books are often more square (~1.2 - 1.4)
    # If the shape doesn't match a standard card, penalize the card score
    if aspect_ratio < 1.35 or aspect_ratio > 1.8:
        score -= 1.0

    # If YOLO originally predicted a book, require overwhelming evidence to flip it to a card
    if class_name == "book":
        score -= 1.0

    # Resolve: need strong agreement to reclassify
    if score >= 2.0:
        # Textured. If it's large, it's a book. Otherwise, card.
        if area_ratio > 0.08:
            return "book"
        return "card"
    elif score <= -2.0:
        # Large + smooth = likely a book; otherwise phone
        if area_ratio > 0.08:
            return "book"
        return "cell phone"

    # Not confident enough to override — keep YOLO's original label
    # However, if YOLO said 'card' but it's large, it's almost certainly a book
    if class_name == "card" and area_ratio > 0.08:
        return "book"

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


def detect(frame, selected_track_id=None):
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
            conf=0.15,
            imgsz=672
        )
    except Exception as e:
        # Fallback to standard inference if tracker fails or is not found
        try:
            results = model(frame, device=device, verbose=False, imgsz=672)
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
                    class_name = custom_classes[cls] if cls < len(custom_classes) else f"class_{cls}"
                    
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

    # Apply select-to-track filtering if a specific ID is selected
    if selected_track_id is not None:
        detections = [d for d in detections if d["id"] == selected_track_id]

    # Draw boxes AFTER resolver has corrected class names
    # (replaces result.plot() which drew uncorrected YOLO labels)
    annotated_frame = draw_cached_boxes(frame, detections)

    return annotated_frame, detections