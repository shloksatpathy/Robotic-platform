import numpy as np
import sys

from audio_utils import record_audio
from embedding import extract_embedding
from speaker_db import SpeakerDatabase
from clustering import cluster_unknown
from vad import detect_speech

def scan_room(duration=5, status_callback=None):
    if status_callback:
        status_callback("Recording...")
    print("\nInitializing Speech Recognition Scanner...")
    db = SpeakerDatabase()
    
    unknown_embeddings_list = []
    detected_known_speakers = set()

    # 1. Capture audio synchronously
    audio = record_audio(duration)
    
    if status_callback:
        status_callback("Processing...")
    print("[Processing] Running Voice Activity Detection...")
    
    # 2. Find all speech segments in the recording
    timestamps = detect_speech(audio, sr=16000)
    
    if not timestamps:
        print("\n--- Final Scan Report ---")
        print("Total Speakers: 0")
        print("-------------------------")
        return

    # 3. Process each segment
    for ts in timestamps:
        segment_audio = audio[ts['start']:ts['end']]
        
        # Skip very short noise blips
        if len(segment_audio) < 16000 * 0.8:
            continue
            
        emb = extract_embedding(segment_audio)
        person = db.identify(emb)
        
        if person:
            detected_known_speakers.add(person)
        else:
            unknown_embeddings_list.append(emb)

    # 4. Cluster unknowns
    if len(unknown_embeddings_list) > 0:
        unknown_matrix = np.vstack(unknown_embeddings_list)
        unknown_speaker_count = cluster_unknown(unknown_matrix)
    else:
        unknown_speaker_count = 0
        
    total = len(detected_known_speakers) + unknown_speaker_count
    
    # 5. Final Report
    print("\n--- Final Scan Report ---")
    print(f"Total Unique Speakers: {total}")
    if detected_known_speakers:
        print(f"Known Speakers Detected: {', '.join(detected_known_speakers)}")
    else:
        print("Known Speakers Detected: None")
    print(f"Unknown Speakers Estimated: {unknown_speaker_count}")
    print("-------------------------")
    
    return {
        "total": total,
        "known": list(detected_known_speakers),
        "unknown": unknown_speaker_count
    }

if __name__ == "__main__":
    scan_duration = 5
    if len(sys.argv) > 1:
        try:
            scan_duration = int(sys.argv[1])
        except ValueError:
            pass
            
    scan_room(scan_duration)