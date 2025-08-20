import os
import sys
import time
import json
import queue
import threading

from core.brain import Brain

# Optional: TTS setup
try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

# Optional: Vosk setup for STT
try:
    from vosk import Model, KaldiRecognizer
    import sounddevice as sd
    HAS_STT = True
except ImportError:
    HAS_STT = False


# ---------------------------
# Boot Display
# ---------------------------
def show_logo():
    logo = r"""
 __  __ _       _       
|  \/  (_)     (_)      
| \  / |_ _ __  _  ___  
| |\/| | | '_ \| |/ _ \ 
| |  | | | | | | | (_) |
|_|  |_|_|_| |_| |\___/ 
               _/ |      
              |__/       
    """
    print("\033[92m" + logo + "\033[0m")


def progress_bar(total=30, delay=0.05, message="Booting Mini 2.0..."):
    print(message)
    for i in range(total + 1):
        bar = "█" * i + "-" * (total - i)
        sys.stdout.write(f"\r[{bar}] {int((i/total)*100)}%")
        sys.stdout.flush()
        time.sleep(delay)
    print("\n")


# ---------------------------
# Mini Class
# ---------------------------
class Mini:
    def __init__(self):
        self.brain = Brain()
        self.use_tts = HAS_TTS
        self.voice_mode = False   # default = text only
        self.running = True
        self.stt_queue = queue.Queue()

        # Setup STT if available
        self.stt_model = None
        if HAS_STT:
            model_path = os.path.join(os.getcwd(), "vosk-model-small-en-in-0.4")
            if os.path.exists(model_path):
                print("[Mini] 🎙 Loading Indian English STT model...")
                try:
                    self.stt_model = Model(model_path)
                    threading.Thread(target=self.background_listener, daemon=True).start()
                    print("[Mini] ✅ Voice Recognition Ready (Indian English)")
                except Exception as e:
                    print(f"[Mini] ❌ Failed to load STT model: {e}")
            else:
                print("[Mini] ⚠ Indian English model not found!")

    # ---------------------------
    # Core Functions
    # ---------------------------
    def speak(self, text):
        """Speak out response if TTS is available"""
        if self.use_tts:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()

    def get_response(self, text: str) -> str:
        """Generate response using Brain"""
        try:
            return self.brain.process(text)
        except Exception as e:
            return f"Error: {str(e)}"

    def background_listener(self):
        """Always listen in background, accept only 'mini ...' commands"""
        try:
            rec = KaldiRecognizer(self.stt_model, 16000)
            with sd.RawInputStream(samplerate=16000, blocksize=8000,
                                   dtype="int16", channels=1) as stream:
                while self.running:
                    data = stream.read(4000)
                    if rec.AcceptWaveform(data[0]):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").strip().lower()
                        if text.startswith("mini"):
                            self.stt_queue.put(text)
        except Exception as e:
            print(f"(STT Error: {str(e)})")

    def run(self):
        """Unified mode: text by default, toggle voice with commands"""
        print("\n[Mini] Running in Text Mode. Type or say 'mini voice mode on' to enable voice.\n")

        while self.running:
            # ---------------- Input (Voice or Text) ----------------
            if not self.stt_queue.empty():
                user_inp = self.stt_queue.get()
                print(f"You (voice): {user_inp}")
            else:
                try:
                    user_inp = input("You: ").strip().lower()
                except EOFError:
                    break

            if not user_inp:
                continue

            # ---------------- Command Handling ----------------
            if user_inp in ["exit", "quit", "mini exit", "mini quit"]:
                print("[Mini] Shutting down...")
                self.running = False
                break

            elif user_inp == "mini voice mode on":
                self.voice_mode = True
                print("[Mini] 🎤 Voice Mode Activated (listening in background).")
                continue

            elif user_inp == "mini voice mode off":
                self.voice_mode = False
                print("[Mini] 🔇 Voice Mode Deactivated (text only).")
                continue

            # ---------------- Normal Conversation ----------------
            if user_inp.startswith("mini"):
                clean_inp = user_inp.replace("mini", "", 1).strip()
            else:
                clean_inp = user_inp

            resp = self.get_response(clean_inp)
            print(f"Mini: {resp}")
            if self.use_tts and self.voice_mode:
                self.speak(resp)


# ---------------------------
# Main Entry
# ---------------------------
if __name__ == "__main__":
    show_logo()
    progress_bar()
    mini = Mini()
    mini.run()
