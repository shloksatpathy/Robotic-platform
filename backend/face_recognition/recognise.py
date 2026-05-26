import cv2
import numpy as np
import os

from insightface.app import FaceAnalysis

# ------------------------------
# CONFIG
# ------------------------------

DATABASE_DIR = "database"
THRESHOLD = 0.45

# ------------------------------
# LOAD MODEL
# ------------------------------

app = FaceAnalysis(
    name="buffalo_s",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(320, 320)
)

# ------------------------------
# LOAD DATABASE
# ------------------------------

database = {}

for file in os.listdir(DATABASE_DIR):

    if file.endswith(".npy"):

        name = file[:-4]

        database[name] = np.load(
            os.path.join(DATABASE_DIR, file)
        )

print("\nLoaded identities:")

for person in database:
    print(person)

# ------------------------------
# SIMILARITY
# ------------------------------

def cosine_similarity(a, b):

    return np.dot(a, b) / (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

# ------------------------------
# IDENTIFICATION
# ------------------------------

def identify(embedding):

    best_name = "Unknown"
    best_score = -1

    for name, db_embedding in database.items():

        score = cosine_similarity(
            embedding,
            db_embedding
        )

        if score > best_score:
            best_score = score
            best_name = name

    if best_score < THRESHOLD:
        return "Unknown", best_score

    return best_name, best_score

# ------------------------------
# CAMERA
# ------------------------------

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    faces = app.get(frame)

    for face in faces:

        x1, y1, x2, y2 = map(
            int,
            face.bbox
        )

        name, score = identify(
            face.embedding
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{name} {score:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    cv2.imshow(
        "Face Recognition",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()