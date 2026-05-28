import sounddevice as sd
import numpy as np

RATE = 16000

def record_audio(duration=3):
    audio=sd.rec(
        int(duration*RATE),
        sample_rate = SAMPLE_RATE,
        channel=1,
        dtype='float32'
    )


    sd.wait()

    return audio.flatten()