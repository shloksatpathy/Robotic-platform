import numpy as np
import os
from audio_utils import record_audio
from embedding import extract_embedding

from vad import detect_speech

name = input("Enter speaker name: ")
audio = record_audio(5)

# Use VAD to crop the audio, stripping silence so it mathematically matches the runtime embeddings
timestamps = detect_speech(audio, sr=16000)
if timestamps:
    # Use the largest speech segment found for the voice print
    ts = max(timestamps, key=lambda t: t['end'] - t['start'])
    audio = audio[ts['start']:ts['end']]
else:
    print("Warning: No speech detected during enrollment! Voice print may be inaccurate.")

emb = extract_embedding(audio)

db_path = os.path.join(os.path.dirname(__file__), "known_speakers.npz")

db = {}
if os.path.exists(db_path):
    with np.load(db_path) as data:
        for key in data.files:
            db[key] = data[key].copy()

db[name] = emb

np.savez(db_path, **db)

print(f"Enrolled speaker: {name}")