import cv2
from detector import detect

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    detections = detect(frame)

    print(detections)

    if cv2.waitKey(1) & 0xff == ord("q"):
        break