import os
import threading
import urllib.request
import wave
import subprocess

# Model URLs (using a fast, medium quality voice en_US-lessac-medium)
MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"

backend_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(backend_dir, "en_US-lessac-medium.onnx")
CONFIG_FILE = os.path.join(backend_dir, "en_US-lessac-medium.onnx.json")

class TTSEngine:
    def __init__(self):
        self._voice = None
        self._lock = threading.Lock()
        self._queue = []
        self._worker_thread = None
        self.is_ready = False

        # Start init thread so it doesn't block server startup
        threading.Thread(target=self._initialize, daemon=True).start()

    def _initialize(self):
        try:
            # Lazy import to avoid crashing if piper is missing
            from piper import PiperVoice
            
            if not os.path.exists(MODEL_FILE):
                print(f"[TTS] Downloading Piper ONNX model to {MODEL_FILE}...")
                urllib.request.urlretrieve(MODEL_URL, MODEL_FILE)
            if not os.path.exists(CONFIG_FILE):
                print(f"[TTS] Downloading Piper config to {CONFIG_FILE}...")
                urllib.request.urlretrieve(CONFIG_URL, CONFIG_FILE)
                
            print("[TTS] Loading Piper model...")
            self._voice = PiperVoice.load(MODEL_FILE, config_path=CONFIG_FILE)
            self.is_ready = True
            print("[TTS] Piper TTS Engine ready.")
        except ImportError:
            print("[TTS] 'piper-tts' module not found. Please install it using 'pip install piper-tts'")
        except Exception as e:
            print(f"[TTS] Error initializing Piper TTS: {e}")

    def speak(self, text):
        if not self.is_ready:
            print(f"[TTS] Not ready (or not installed), falling back to basic TTS for: {text}")
            self._fallback_speak(text)
            return
            
        with self._lock:
            self._queue.append(text)
            if self._worker_thread is None or not self._worker_thread.is_alive():
                self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
                self._worker_thread.start()

    def _process_queue(self):
        while True:
            with self._lock:
                if not self._queue:
                    break
                text = self._queue.pop(0)
                
            try:
                out_path = os.path.join(backend_dir, "tts_output.wav")
                # Need to use wave.open directly
                with wave.open(out_path, "wb") as wav_file:
                    self._voice.synthesize(text, wav_file)
                    
                # Play the generated audio file
                if os.name == 'nt':
                    import winsound
                    winsound.PlaySound(out_path, winsound.SND_FILENAME)
                else:
                    # 'aplay' is standard ALSA player on Jetson/Linux
                    subprocess.run(["aplay", "-q", out_path])
            except Exception as e:
                print(f"[TTS] Error synthesizing/playing speech: {e}")

    def _fallback_speak(self, text):
        try:
            if os.name == 'nt':
                subprocess.Popen([
                    "powershell", "-Command",
                    f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}');"
                ], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
            else:
                subprocess.Popen(["espeak", text])
        except Exception as tts_e:
            print(f"[ERROR] Fallback TTS failed: {tts_e}")

# Global instance
tts = TTSEngine()

def speak_async(text):
    tts.speak(text)
