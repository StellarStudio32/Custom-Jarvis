"""
Text-to-Speech action module using pyttsx3.
Runs a background thread with a queue to avoid blocking the main thread.
"""

import threading
import queue
import time
import os
import subprocess

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

import config


class TTSWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.q = queue.Queue()
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        if pyttsx3 is None:
            return
        
        # Try eSpeak first (more voices available)
        espeak_dir = r"C:\Program Files (x86)\eSpeak"
        espeak_exe = os.path.join(espeak_dir, "command_line", "espeak.exe")
        espeak_data = os.path.join(espeak_dir, "espeak-data")
        
        if os.path.exists(espeak_exe) and os.path.exists(espeak_data):
            try:
                # Set environment variables for eSpeak
                original_path = os.environ.get('PATH', '')
                os.environ['PATH'] = os.path.join(espeak_dir, "command_line") + os.pathsep + original_path
                os.environ['ESPEAK_DATA_PATH'] = espeak_data
                
                # Test by running espeak directly before initializing pyttsx3
                result = subprocess.run(
                    [espeak_exe, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    cwd=espeak_dir  # Change working directory to espeak folder
                )
                
                if result.returncode == 0:
                    # eSpeak works, try pyttsx3
                    self.engine = pyttsx3.init(driverName='espeak')
                    voices = self.engine.getProperty('voices')
                    if voices and config.TTS_VOICE_INDEX < len(voices):
                        self.engine.setProperty('voice', voices[config.TTS_VOICE_INDEX].id)
                    self.engine.setProperty('rate', config.TTS_RATE)
                    print(f"✓ TTS: Using eSpeak (voice {config.TTS_VOICE_INDEX}, rate {config.TTS_RATE})")
                    return
            except Exception as e:
                print(f"⚠ eSpeak init: {type(e).__name__} - will use SAPI instead")
        
        # Fallback to Windows SAPI (built-in, always available, recommended)
        try:
            self.engine = pyttsx3.init()  # Uses Windows SAPI driver by default
            voices = self.engine.getProperty('voices')
            if voices and config.TTS_VOICE_INDEX < len(voices):
                self.engine.setProperty('voice', voices[config.TTS_VOICE_INDEX].id)
            self.engine.setProperty('rate', config.TTS_RATE)
            print(f"✓ TTS: Using Windows SAPI (voice {config.TTS_VOICE_INDEX}, rate {config.TTS_RATE})")
        except Exception as e:
            print(f"✗ TTS initialization failed: {e}")
            self.engine = None

    def run(self):
        while True:
            try:
                text = self.q.get()
                if text is None:
                    break
                if not self.engine:
                    # Fallback: print if engine unavailable
                    print(f"TTS: {text}")
                    continue
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
            finally:
                time.sleep(0.01)


_tts_worker = TTSWorker()
_tts_worker.start()


def speak(text: str) -> None:
    """Queue text to speak asynchronously."""
    try:
        _tts_worker.q.put_nowait(text)
    except Exception as e:
        print(f"Failed to enqueue TTS text: {e}")



