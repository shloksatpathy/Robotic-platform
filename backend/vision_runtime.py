import cv2
import time

from detector import detect
from face.recognise import FaceRecognizer
from face.enroll import EnrollmentSession


# ----------------------------------
# CONFIG
# ----------------------------------

RECOGNITION_REFRESH_SEC = 5

# ----------------------------------
# FACE RECOGNIZER
# ----------------------------------

recognizer = FaceRecognizer()

# track_id -> identity cache
track_identity_cache = {}

# ----------------------------------
# CAMERA
# ----------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Failed to open camera")

print("[SYSTEM] Vision runtime started")
print("[N] Enroll person")
print("[Q] Quit")

# ----------------------------------
# ENROLLMENT STATE
# ----------------------------------

enrollment_session = None

# ----------------------------------
# MAIN LOOP
# ----------------------------------

while True:

    ret, frame = cap.read()

    if not ret:
        break

    current_time = time.time()

    # -----------------------------
    # ENROLLMENT MODE
    # -----------------------------

    if enrollment_session is not None:

        if enrollment_session.is_active():

            # Feed frame to enrollment session
            annotated_frame = enrollment_session.process_frame(
                frame.copy()
            )

            cv2.imshow(
                "Vision Runtime",
                annotated_frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                enrollment_session.cancel()
                enrollment_session = None
                print("[INFO] Resuming detection")

            continue

        # Enrollment just finished
        if enrollment_session.is_complete():

            enrollment_session.save()
            recognizer.reload_database()

            # Clear identity cache so new person
            # gets recognized immediately
            track_identity_cache.clear()

            print("[INFO] Database reloaded")

        enrollment_session = None
        print("[INFO] Resuming detection")
        continue

    # -----------------------------
    # YOLO + BYTE TRACK
    # -----------------------------

    annotated_frame, detections = detect(frame)

    # -----------------------------
    # FACE RECOGNITION
    # -----------------------------

    for det in detections:

        if det["class"] != "person":
            continue

        track_id = det["id"]

        if track_id is None:
            continue

        should_recognize = False

        if track_id not in track_identity_cache:
            should_recognize = True

        else:

            elapsed = (
                current_time
                -
                track_identity_cache[track_id]["last_update"]
            )

            if elapsed > RECOGNITION_REFRESH_SEC:
                should_recognize = True

        # -------------------------
        # RECOGNIZE
        # -------------------------

        if should_recognize:

            try:

                name, score = recognizer.recognize_person(
                    frame,
                    det["box"]
                )

                track_identity_cache[track_id] = {
                    "name": name,
                    "score": score,
                    "last_update": current_time
                }

            except Exception as e:

                print(
                    f"[ERROR] Recognition failed: {e}"
                )

        # -------------------------
        # DRAW IDENTITY
        # -------------------------

        if track_id in track_identity_cache:

            identity = track_identity_cache[
                track_id
            ]

            x1, y1, x2, y2 = det["box"]

            label = (
                f'{identity["name"]} '
                f'({identity["score"]:.2f})'
            )

            cv2.putText(
                annotated_frame,
                label,
                (x1, max(20, y1 - 30)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 255),
                2
            )

    # -----------------------------
    # HUD
    # -----------------------------

    cv2.putText(
        annotated_frame,
        "N = Enroll | Q = Quit",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.imshow(
        "Vision Runtime",
        annotated_frame
    )

    # -----------------------------
    # KEYBOARD
    # -----------------------------

    key = cv2.waitKey(1) & 0xFF

    # Quit

    if key == ord("q"):
        break

    # Enroll

    elif key == ord("n"):

        print("\n=== ENROLLMENT ===")

        name = input(
            "Enter person name: "
        ).strip()

        if len(name):

            print(
                f"Starting enrollment for {name}"
            )

            enrollment_session = EnrollmentSession(
                name,
                recognizer=recognizer
            )

# ----------------------------------
# CLEANUP
# ----------------------------------

cap.release()

cv2.destroyAllWindows()