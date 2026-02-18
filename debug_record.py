"""
Debug recording helper
Records a short WAV to the `workspace/` folder and runs the transcriber for quick diagnosis.
Run: python debug_record.py [seconds]
"""

import sys
from pathlib import Path
import sounddevice as sd
import wave
import struct
import config
from transcriber import transcribe


def main():
    seconds = 5
    if len(sys.argv) > 1:
        try:
            seconds = int(sys.argv[1])
        except Exception:
            pass

    sr = 16000
    print(f"Recording {seconds}s at {sr}Hz...")
    data = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype='float32')
    sd.wait()

    # Save as 16-bit WAV
    out_path = Path(config.WORKSPACE_DIR) / "debug.wav"
    
    # Flatten data and convert to 16-bit PCM
    if hasattr(data, 'flatten'):
        flat_data = data.flatten()
    else:
        flat_data = data if isinstance(data, list) else list(data)
    
    # Convert float32 to 16-bit signed integer
    pcm16 = struct.pack('<' + 'h' * len(flat_data), *[int(s * 32767) for s in flat_data])
    
    with wave.open(str(out_path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16)

    print(f"Saved debug WAV: {out_path}")
    print("Attempting transcription (may download model on first run)...")
    transcript = transcribe(data, sample_rate=sr)
    print("Transcript:", repr(transcript))


if __name__ == '__main__':
    main()
