import cv2
import torch
from ultralytics import YOLO

# Detect best available hardware device (GPU CUDA vs CPU fallback)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[SYSTEM] Initializing YOLOv8n engine on device: {device.upper()}")

try:
    model = YOLO("yolov8s-world.pt")

    model.set_classes([
    # Human related
    "person",
    "hand",
    "arm",
    "head",
    "face",

    # Computers & electronics
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
    "earphones",
    "router",
    "circuit board",
    "battery",
    "charger",
    "charging cable",
    "usb drive",

    # Furniture
    "chair",
    "couch",
    "desk",
    "table",
    "cabinet",
    "drawer",
    "bookshelf",

    # Stationery
    "pen",
    "pencil",
    "marker",
    "notebook",
    "book",
    "paper",
    "document",
    "folder",
    "calendar",
    "sticky note",

    # Personal items
    "backpack",
    "handbag",
    "wallet",
    "suitcase",
    "glasses",
    "watch",
    "keys",
    "id card",

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
            verbose=False
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
        # Draw bounding boxes onto the frame using YOLO's native plotter
        try:
            annotated_frame = result.plot()
        except Exception as e:
            print(f"Error plotting annotations: {e}")

        # Extract details including raw box coordinates for interpolation/caching
        if result.boxes is not None:
            for box in result.boxes:
                if box.cls is not None and len(box.cls) > 0:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0]) if box.conf is not None else 0.0
                    class_name = model.names[cls]
                    
                    # Grab coordinates [x1, y1, x2, y2]
                    coords = box.xyxy[0].tolist() if box.xyxy is not None else [0, 0, 0, 0]
                    # Get tracking ID if available
                    track_id = int(box.id[0].item()) if box.id is not None else None
                    
                    detections.append({
                        "id": track_id,
                        "class": class_name,
                        "confidence": round(conf, 2),
                        "box": [int(c) for c in coords]
                    })

    return annotated_frame, detections

# Dynamic color map for drawing cached boxes
CLASS_COLORS = {
    "person": (255, 180, 0),      # Cyber Cyan/Blue BGR
    "sports ball": (0, 255, 120),  # Neon Green BGR
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