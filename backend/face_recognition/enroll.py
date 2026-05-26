import cv2
import numpy as np
import os
import time

from insightface.app import FaceAnalysis

# --------------------------------
# CONFIG
# --------------------------------

DATABASE_DIR = "database"
NUM_SAMPLES = 30
MIN_FACE_SIZE = 120

os.makedirs(DATABASE_DIR, exist_ok=True)

# --------------------------------
# LOAD MODEL
# --------------------------------

app = FaceAnalysis(
    name="buffalo_s",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(320, 320)
)

# --------------------------------
# NAME
# --------------------------------

person_name = input("Enter person name: ").strip()

if not person_name:
    raise ValueError("Invalid name")

# --------------------------------
# CAMERA
# --------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Camera not opened")

print(f"\nCollecting {NUM_SAMPLES} samples...")
print("Look at camera and slowly move head.")
print("Press Q to cancel.\n")

embeddings = []
last_capture = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    faces = app.get(frame)

    for face in faces:

        x1, y1, x2, y2 = map(int, face.bbox)

        width = x2 - x1
        height = y2 - y1

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Samples: {len(embeddings)}/{NUM_SAMPLES}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Ignore tiny faces
        if width < MIN_FACE_SIZE or height < MIN_FACE_SIZE:
            continue

        current_time = time.time()

        # Capture every 0.3 sec
        if current_time - last_capture > 0.3:

            embeddings.append(face.embedding)

            last_capture = current_time

            print(
                f"Captured {len(embeddings)}/{NUM_SAMPLES}"
            )

    cv2.imshow("Enrollment", frame)

    if len(embeddings) >= NUM_SAMPLES:
        break

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

# --------------------------------
# SAVE PROFILE
# --------------------------------

if len(embeddings) == 0:
    raise RuntimeError("No samples collected")

mean_embedding = np.mean(
    np.array(embeddings),
    axis=0
)

save_path = os.path.join(
    DATABASE_DIR,
    f"{person_name.lower()}.npy"
)

np.save(
    save_path,
    mean_embedding
)

print(f"\nSaved profile:")
print(save_path)
print(f"Samples used: {len(embeddings)}")