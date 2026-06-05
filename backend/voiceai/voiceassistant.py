import pyaudio
import numpy as np
from openwakeword.model import Model
from openwakeword.utils import download_models
from faster_whisper import WhisperModel
import speech_recognition as sr
import subprocess
from ollama import chat
import os

# ---------------------------------------------------------
# NOTE ON WAKE WORD:
# You requested "hey rover", but openWakeWord does not have
# a built-in model for that phrase. To use "hey rover",
# you will need to generate a custom .onnx model (e.g., via 
# https://huggingface.co/spaces/davidscripka/openWakeWord)
# and load it by passing the path: wakeword_models=["path/to/hey_rover.onnx"]
#
# For now, we are using the built-in "hey_jarvis" model to 
# ensure the pipeline works out-of-the-box.
# ---------------------------------------------------------

print("Initializing Wake Word model...")
download_models()
# Initialize OpenWakeWord
oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

print("Initializing Faster-Whisper model...")
# Initialize Faster-Whisper (downloads the 'base.en' model on first run)
whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")

# Initialize SpeechRecognition for Voice Activity Detection
recognizer = sr.Recognizer()

# PyAudio setup for Wake Word listening
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280
audio = pyaudio.PyAudio()

def listen_for_wakeword():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("\nListening for wake word 'hey jarvis'...")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Predict wake word
            prediction = oww_model.predict(audio_data)
            
            # Check if any wakeword passed the threshold
            for wakeword, score in prediction.items():
                if score > 0.5:
                    print(f"\nWake word detected! Score: {score}")
                    return
    finally:
        stream.stop_stream()
        stream.close()

def record_and_transcribe():
    with sr.Microphone(sample_rate=16000) as source:
        print("Adjusting for ambient noise... (1 sec)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Speak now!")
        
        # Audio cue acknowledging the wake word
        subprocess.run([
            "powershell", "-Command", 
            "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('Yes?');"
        ], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
        
        try:
            # Listen until silence is detected
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            
            # Save to temporary file for faster-whisper
            temp_file = "temp_audio.wav"
            with open(temp_file, "wb") as f:
                f.write(audio_data.get_wav_data())
            
            print("Transcribing...")
            segments, info = whisper_model.transcribe(temp_file, beam_size=5)
            transcription = "".join([segment.text for segment in segments])
            
            print("You:", transcription)
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            return transcription
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None
        except Exception as e:
            print("Error recording/transcribing:", e)
            return None

def main():
    while True:
        listen_for_wakeword()
        prompt = record_and_transcribe()
        
        if prompt and prompt.strip():
            print("Thinking...")
            # Send to Ollama
            response = chat(
                model='qwen2.5:3B-instruct',
                messages=[{'role': 'user', 'content': prompt}]
            )
            reply = response['message']['content']
            print("Assistant:", reply)
            
            safe_reply = reply.replace("'", "''").replace("\n", " ").replace("\r", "")
            subprocess.run([
                "powershell", "-Command",
                f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_reply}');"
            ], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))

if __name__ == "__main__":
    main()