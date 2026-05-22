"""import cv2
from detector import detect

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    detections = detect(frame)

    print(detections)

    cv2.imshow()

    if cv2.waitKey(1) & 0xff == ord("q"):
        break"""

import cv2
from detector import detect

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    annotated_frame, detections = detect(frame)

    print(detections)

    cv2.imshow("YOLO Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()