from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect(frame):

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml"
    )

    detections = []

    for result in results:
        for box in result.boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])

            detections.append({
                "class": model.names[cls],
                "confidence": round(conf, 2)
            })
    return detections
       