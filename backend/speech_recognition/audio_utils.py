import sounddevice as sd
import numpy as np

def record_audio(duration=5):
    print(f"[Mic] Recording for {duration} seconds...")

    try:
        audio = sd.rec(
            int(duration * 16000),
            samplerate=16000,
            channels=1,
            device=1,
            dtype='float32'
        )
        sd.wait()
    except Exception as e:
        print(f"[Mic] Warning: Failed to record with device=1 ({e}). Trying default input device...")
        try:
            audio = sd.rec(
                int(duration * 16000),
                samplerate=16000,
                channels=1,
                device=None,
                dtype='float32'
            )
            sd.wait()
        except Exception as e2:
            print(f"[Mic] Error: Failed to record with default input device ({e2})")
            raise e2

    audio = audio.flatten()
    
    # Normalize enrollment audio to match runtime audio
    peak = np.abs(audio).max()
    if peak > 0.001:
        audio = audio / peak * 0.9
        
    return audio