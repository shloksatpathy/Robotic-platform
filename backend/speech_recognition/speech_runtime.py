import faiss
import numpy as np
import os
from audio_utils import record_audio
from embedding import extract_embedding
from clustering import cluster_unknown


THRESHOLD = 0.75
dimension=192

index = faiss.indexFlatL2(dimension)

known_names = []


for file in os.listdir("known_db"):

    emb = np.load(f"load_db/{file}").astype('float32')

    index.add(np.array([emb]))

    known_names.append(file.replace(".npy", ""))

def identify_speaker(embedding):

    emb = np.array([embedding]).astype('float32')

    D, I = index.search(emb, 1)

    similarity = 1 / (1 + D[0][0])

    if similarity > THRESHOLD:
        return known_names[I[0][0]]

    return "unknown"


unknown_embeddings = []

while True:

    audio = record_audio(duration=3)

    speech = detect_speech(audio)

    if len(speech) == 0:
        continue

    emb = extract_embedding(audio)

    identity = identify_speaker(emb)

    if identity == "unknown":

        unknown_embeddings.append(emb)

        count = cluster_unknowns(
            np.array(unknown_embeddings)
        )

        print(f"Unknown speakers: {count}")

    else:

        print(f"Known speaker: {identity}") 