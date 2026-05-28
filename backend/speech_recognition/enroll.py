import numpy as np
from audio_utils import record_chunk
from embeddings import extract_embeddings

name=input("speaker-name: ")

audio = record_chunk(duration=5)

embeddings = extract_embedding(audio)

np.save(f"known_db/{name}.npy", embeddings)

print("speaker enrolled ")