import cv2
import time
import datetime
import subprocess

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

# Replace with the exact RTSP or HTTP stream URL for your IP camera
# e.g., "rtsp://192.168.144.108:554/stream1" or "http://192.168.144.108/video"
CAMERA_SOURCE = "http://192.168.144.108/" 

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError(f"Failed to open camera stream at {CAMERA_SOURCE}")

print("[SYSTEM] Vision runtime started")
print("[N] Enroll person")
print("[Q] Quit")

# ----------------------------------
# ENROLLMENT STATE
# ----------------------------------

enrollment_session = None

# ----------------------------------
# GREETING STATE
# ----------------------------------

greeted_today = {}

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

                # Greet the person if recognized and not yet greeted today
                if name != "Unknown":
                    today = datetime.date.today()
                    if greeted_today.get(name) != today:
                        greeted_today[name] = today
                        print(f"[GREETING] Hello, {name}")
                        try:
                            # Use PowerShell for non-blocking TTS on Windows without extra dependencies
                            subprocess.Popen([
                                "powershell", "-Command",
                                f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('Hello {name}');"
                            ], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
                        except Exception as tts_e:
                            print(f"[ERROR] TTS failed: {tts_e}")

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

        # In-window name input (no terminal needed)
        input_name = ""
        entering = True

        while entering:

            ret2, input_frame = cap.read()

            if not ret2:
                break

            # Dark overlay
            overlay = input_frame.copy()
            cv2.rectangle(
                overlay,
                (0, 0),
                (overlay.shape[1], overlay.shape[0]),
                (0, 0, 0),
                -1
            )
            cv2.addWeighted(
                overlay, 0.6,
                input_frame, 0.4,
                0, input_frame
            )

            # Title
            cv2.putText(
                input_frame,
                "ENROLL NEW PERSON",
                (input_frame.shape[1] // 2 - 180, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2
            )

            # Prompt
            cv2.putText(
                input_frame,
                "Type name and press ENTER:",
                (input_frame.shape[1] // 2 - 200, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (200, 200, 200),
                1
            )

            # Input field background
            field_x = input_frame.shape[1] // 2 - 200
            field_y = 230
            cv2.rectangle(
                input_frame,
                (field_x, field_y),
                (field_x + 400, field_y + 50),
                (40, 40, 40),
                -1
            )
            cv2.rectangle(
                input_frame,
                (field_x, field_y),
                (field_x + 400, field_y + 50),
                (0, 255, 255),
                2
            )

            # Typed text with blinking cursor
            cursor = "_" if int(time.time() * 2) % 2 else " "
            cv2.putText(
                input_frame,
                input_name + cursor,
                (field_x + 15, field_y + 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )

            # Hint
            cv2.putText(
                input_frame,
                "ESC = Cancel",
                (input_frame.shape[1] // 2 - 70, 330),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (100, 100, 100),
                1
            )

            cv2.imshow("Vision Runtime", input_frame)

            k = cv2.waitKey(30) & 0xFF

            # Enter key — confirm
            if k == 13:
                entering = False

            # Escape — cancel
            elif k == 27:
                input_name = ""
                entering = False

            # Backspace
            elif k == 8:
                input_name = input_name[:-1]

            # Printable ASCII characters
            elif 32 <= k <= 126:
                input_name += chr(k)

        name = input_name.strip()

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