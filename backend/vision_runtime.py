import cv2
import time
import datetime
import subprocess
import sys
import os
import threading
import queue
import subprocess

# Add speech recognition folder to system path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "speech_recognition"))

from detector import detect
from face.recognise import FaceRecognizer
from face.enroll import EnrollmentSession
from speech_runtime import scan_room


# ----------------------------------
# CONFIG
# ----------------------------------

RECOGNITION_REFRESH_SEC = 5

# ----------------------------------
# SELECTION TRACKING
# ----------------------------------

selected_track_id = None
current_detections = []

def mouse_callback(event, x, y, flags, param):
    global selected_track_id, current_detections
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_box = False
        for det in current_detections:
            x1, y1, x2, y2 = det["box"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                selected_track_id = det["id"]
                clicked_box = True
                print(f"[INFO] Locked tracking onto ID: {selected_track_id}")
                break
        
        if not clicked_box:
            selected_track_id = None
            print("[INFO] Cleared tracking lock")

# Register window and callback early
cv2.namedWindow("Vision Runtime")
cv2.setMouseCallback("Vision Runtime", mouse_callback)

# ----------------------------------
# FACE RECOGNIZER
# ----------------------------------

recognizer = FaceRecognizer()

# track_id -> identity cache
track_identity_cache = {}

# ----------------------------------
# SPEECH RECOGNITION STATE
# ----------------------------------

speech_status = "Idle"
speech_results = None
speech_thread = None

def set_speech_status(status):
    global speech_status
    speech_status = status

def run_speech_scan(duration=5):
    global speech_status, speech_results
    try:
        results = scan_room(duration, status_callback=set_speech_status)
        speech_results = results
        speech_status = "Idle"
    except Exception as e:
        print(f"[ERROR] Speech scan failed: {e}")
        speech_status = "Error"
        time.sleep(2)
        speech_status = "Idle"

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

last_seen_time = {}
greeting_queue = queue.Queue()

def tts_worker():
    while True:
        name = greeting_queue.get()
        if name is None:
            break
        print(f"[GREETING] Hello, {name}")
        """
        For speech on windown uncomment the powershell part and comment the echo part and 
        vice versa for arm ubuntu (jetson nano) 
        """
        try:
            # Use synchronous subprocess.run to block until speaking finishes
            subprocess.run([
            #     "powershell", "-Command",
            #     f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('Hello {name}');"
                  f'echo"{text}"| piper --model en-US-lessac-medium.onnx --output_raw | aplay -r 22050 -f S16_LE pt raw''
                  shell = True
             ], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
        except Exception as tts_e:
            print(f"[ERROR] TTS failed: {tts_e}")
        greeting_queue.task_done()

tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

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

    annotated_frame, detections = detect(frame, selected_track_id=selected_track_id)
    current_detections = detections

    # -----------------------------
    # FACE RECOGNITION
    # -----------------------------
    
    visible_names_this_frame = set()

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

            # Collect visible names this frame
            if identity["name"] != "Unknown":
                visible_names_this_frame.add(identity["name"])

    # Process Greetings for visible people
    for name in visible_names_this_frame:
        last_seen = last_seen_time.get(name, 0)
        if current_time - last_seen > 5:  # 5 seconds cooldown
            greeting_queue.put(name)
        last_seen_time[name] = current_time

    # -----------------------------
    # HUD
    # -----------------------------

    cv2.putText(
        annotated_frame,
        "N = Enroll | Q = Quit | S = Scan Voice",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    # Draw Speech Scan Status / Results
    if speech_status != "Idle":
        color = (0, 165, 255)  # Orange for active recording / processing
        cv2.putText(
            annotated_frame,
            f"[Speech Scan] {speech_status}",
            (10, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )
    elif speech_results is not None:
        color = (0, 255, 0)  # Green for results
        known_str = ", ".join(speech_results["known"]) if speech_results["known"] else "None"
        res_str = f"Last Scan: {speech_results['total']} Spk (Known: {known_str}, Unk: {speech_results['unknown']})"
        cv2.putText(
            annotated_frame,
            res_str,
            (10, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
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

    # Scan Speech
    elif key == ord("s"):
        if speech_thread is None or not speech_thread.is_alive():
            print("[INFO] Starting speech recognition scan in background...")
            speech_thread = threading.Thread(
                target=run_speech_scan,
                args=(5,),
                daemon=True
            )
            speech_thread.start()

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