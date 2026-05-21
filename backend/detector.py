import cv2
from ultralytics import YOLO

# Load YOLOv8 model
try:
    model = YOLO("yolov8n.pt")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

def detect(frame):
    """
    Runs YOLOv8 object tracking on the input frame.
    Returns:
        annotated_frame (numpy.ndarray): Frame with plotted bounding boxes.
        detections (list): List of detected objects with class and confidence.
    """
    if model is None:
        return frame, []

    try:
        # Run tracking using ByteTrack
        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml"
        )
    except Exception as e:
        # Fallback to standard inference if tracker fails or is not found
        try:
            results = model(frame)
        except Exception as ex:
            print(f"Error during YOLO detection: {ex}")
            return frame, []

    detections = []
    annotated_frame = frame.copy()

    if results and len(results) > 0:
        result = results[0]
        # Draw bounding boxes onto the frame
        try:
            annotated_frame = result.plot()
        except Exception as e:
            print(f"Error plotting annotations: {e}")

        # Extract detections list for the frontend
        if result.boxes is not None:
            for box in result.boxes:
                if box.cls is not None and len(box.cls) > 0:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0]) if box.conf is not None else 0.0
                    class_name = model.names[cls]
                    
                    detections.append({
                        "class": class_name,
                        "confidence": round(conf, 2)
                    })

    return annotated_frame, detections