import cv2
import time
import datetime
import sys
import os
import threading
import subprocess
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

# Add speech recognition folder to system path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "speech_recognition"))

from detector import detect
from face.recognise import FaceRecognizer
from speech_runtime import scan_room
from tts_engine import speak_async

app = Flask(__name__)
CORS(app)

# ----------------------------------
# STATE VARIABLES
# ----------------------------------
selected_track_id = None
current_detections = []

speech_status = "Idle"
speech_results = None
speech_thread = None


recognizer = FaceRecognizer()
track_identity_cache = {}
last_seen_time = {}

RECOGNITION_REFRESH_SEC = 5

latest_jpeg = None
lock = threading.Lock()

# Stats for the dashboard
stats_data = {
    "fps": 0.0,
    "status": "running",
    "person_count": 0,
    "object_count": 0,
    "id_card_count": 0
}
last_frame_time = time.time()

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

def video_processing_loop():
    global latest_jpeg, selected_track_id, current_detections
    global recognizer, track_identity_cache, last_seen_time
    global speech_status, speech_results, speech_thread
    global stats_data, last_frame_time

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Failed to open camera stream.")
        return

    print("[SYSTEM] Headless Vision Server started.")

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue

        current_time = time.time()
        fps = 1.0 / (current_time - last_frame_time) if current_time - last_frame_time > 0 else 0.0
        last_frame_time = current_time

        # -----------------------------
        # YOLO + BYTE TRACK
        # -----------------------------
        annotated_frame, detections = detect(frame, selected_track_id=selected_track_id)
        current_detections = detections

        person_count = sum(1 for d in detections if d["class"] == "person")
        object_count = len(detections) - person_count
        id_card_count = sum(1 for d in detections if d["class"] == "id_card")

        stats_data["fps"] = fps
        stats_data["person_count"] = person_count
        stats_data["object_count"] = object_count
        stats_data["id_card_count"] = id_card_count

        # -----------------------------
        # FACE RECOGNITION & GREETINGS
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
                elapsed = current_time - track_identity_cache[track_id]["last_update"]
                if elapsed > RECOGNITION_REFRESH_SEC:
                    should_recognize = True

            if should_recognize:
                try:
                    name, score = recognizer.recognize_person(frame, det["box"])
                    track_identity_cache[track_id] = {
                        "name": name,
                        "score": score,
                        "last_update": current_time
                    }
                except Exception as e:
                    print(f"[ERROR] Recognition failed: {e}")

            # Draw Identity and collect visible names
            if track_id in track_identity_cache:
                identity = track_identity_cache[track_id]
                x1, y1, x2, y2 = det["box"]
                
                name = identity["name"]
                if name != "Unknown":
                    visible_names_this_frame.add(name)

                label = f'{name} ({identity["score"]:.2f})'
                cv2.putText(annotated_frame, label, (x1, max(20, y1 - 30)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        # Process Greetings for visible people
        for name in visible_names_this_frame:
            last_seen = last_seen_time.get(name, 0)
            if current_time - last_seen > 5:  # 5 seconds cooldown
                print(f"[GREETING] Hello, {name}")
                speak_async(f"Hello {name}")
            
            # Update last seen time while they remain in frame
            last_seen_time[name] = current_time

        # Draw Speech Scan Status / Results
        if speech_status != "Idle":
            color = (0, 165, 255)  
            cv2.putText(annotated_frame, f"[Speech Scan] {speech_status}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        elif speech_results is not None:
            color = (0, 255, 0)
            known_str = ", ".join(speech_results["known"]) if speech_results["known"] else "None"
            res_str = f"Last Scan: {speech_results['total']} Spk (Known: {known_str}, Unk: {speech_results['unknown']})"
            cv2.putText(annotated_frame, res_str, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Encode to JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if ret:
            with lock:
                latest_jpeg = buffer.tobytes()

# ----------------------------------
# FLASK ROUTES
# ----------------------------------

@app.route('/video_feed')
def video_feed():
    """Streams MJPEG from the video processing thread."""
    def generate():
        while True:
            with lock:
                if latest_jpeg is None:
                    continue
                frame_bytes = latest_jpeg
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03) # ~30 fps cap
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/scan_speech', methods=['POST'])
def api_scan_speech():
    """Triggers speech recognition scan."""
    global speech_thread
    if speech_thread is None or not speech_thread.is_alive():
        print("[INFO] Starting speech recognition scan from API...")
        speech_thread = threading.Thread(target=run_speech_scan, args=(5,), daemon=True)
        speech_thread.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already_running"}), 400

@app.route('/api/enroll', methods=['POST'])
def api_enroll():
    """Receives an .npy embedding file and saves it to the database."""
    name = request.form.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400
        
    if 'embedding' not in request.files:
        return jsonify({"error": "No embedding file provided"}), 400
        
    file = request.files['embedding']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and file.filename.endswith('.npy'):
        db_dir = os.path.join(os.path.dirname(__file__), "face", "database")
        os.makedirs(db_dir, exist_ok=True)
        save_path = os.path.join(db_dir, f"{name}.npy")
        file.save(save_path)
        
        print(f"[INFO] Saved new embedding for {name}")
        recognizer.reload_database()
        track_identity_cache.clear()
        
        return jsonify({"status": f"successfully enrolled {name}"})
        
    return jsonify({"error": "Invalid file format. Expected .npy"}), 400

@app.route('/api/track', methods=['POST'])
def api_track():
    """Updates selected tracking ID based on web dashboard click coordinates."""
    global selected_track_id, current_detections
    data = request.json
    
    if not data:
        return jsonify({"error": "no data provided"}), 400
        
    if "clear" in data and data["clear"]:
        selected_track_id = None
        print("[INFO] Cleared tracking lock via API")
        return jsonify({"status": "cleared"})
        
    x = data.get("x")
    y = data.get("y")
    
    if x is not None and y is not None:
        clicked_box = False
        for det in current_detections:
            x1, y1, x2, y2 = det["box"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                selected_track_id = det["id"]
                clicked_box = True
                print(f"[INFO] Locked tracking onto ID: {selected_track_id} via API")
                break
                
        if not clicked_box:
            selected_track_id = None
            print("[INFO] Cleared tracking lock via API")
            
    return jsonify({"status": "updated", "selected_track_id": selected_track_id})

@app.route('/api/state', methods=['GET'])
def api_state():
    """Returns general state for the dashboard."""
    return jsonify({
        "selected_track_id": selected_track_id,
        "speech_status": speech_status
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Returns YOLO statistics for the frontend AI panel."""
    return jsonify(stats_data)

if __name__ == '__main__':
    # Start the OpenCV camera processing thread
    vt = threading.Thread(target=video_processing_loop, daemon=True)
    vt.start()
    
    # Run the Flask web server
    app.run(host='0.0.0.0', port=5000, threaded=True)
