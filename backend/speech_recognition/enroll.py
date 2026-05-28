import numpy as np
from audio_utils import record_audio
from embeddings import extract_embeddings

name=input("speaker-name: ")

audio = record_audio(duration=5)

embeddings = extract_embedding(audio)

np.save(f"known_db/{name}.npy", embeddings)

print("speaker enrolled ")