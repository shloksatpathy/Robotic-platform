import sounddevice as sd
import numpy as np

def record_audio(duration=5):
    print(f"[Mic] Recording for {duration} seconds...")

    audio = sd.rec(
        int(duration * 16000),
        samplerate=16000,
        channels=1,
        device=1,
        dtype='float32'
    )

    sd.wait()
    audio = audio.flatten()
    
    # Normalize enrollment audio to match runtime audio
    peak = np.abs(audio).max()
    if peak > 0.001:
        audio = audio / peak * 0.9
        
    return audio