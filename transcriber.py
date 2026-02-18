"""
Transcriber Module
Transcribes audio using faster-whisper (runs offline after first download).
Model is cached after first load.
"""

from faster_whisper import WhisperModel
import config
import wave
import tempfile
import struct
from pathlib import Path
import traceback

# Global model cache
_model = None


def _get_model() -> WhisperModel:
    """
    Get or initialize the Whisper model.
    Model is cached after first load to avoid reloading.
    
    Returns:
        WhisperModel instance
    """
    global _model
    if _model is None:
        # Initialize model (downloads on first run)
        print(f"Loading Whisper model '{config.WHISPER_MODEL}'... (first run may take a minute or two)")
        _model = WhisperModel(config.WHISPER_MODEL, device="auto", compute_type="auto")
    return _model


def transcribe(audio_buffer, sample_rate: int = 16000) -> str:
    """
    Transcribe audio buffer using faster-whisper with basic preprocessing.

    Args:
        audio_buffer: Audio samples (list, array, or similar sequence of float32)
        sample_rate: Sample rate of the audio buffer (default 16000)

    Returns:
        Transcribed text (lowercase). Returns empty string on failure.
    """
    try:
        if audio_buffer is None:
            print("Transcription called with None audio_buffer")
            return ""

        # Convert to list if needed (faster-whisper will handle it)
        audio = audio_buffer

        # Handle multi-dimensional sequences
        if hasattr(audio, 'ndim'):  # numpy array
            if audio.ndim > 1:
                audio = audio.flatten()
        else:  # list or similar
            if isinstance(audio, (list, tuple)):
                audio = list(audio)

        duration_sec = len(audio) / float(sample_rate) if sample_rate else 0.0
        print(f"Transcribing audio: samples={len(audio)}, duration={duration_sec:.2f}s")

        # Too short -> skip
        if len(audio) < 1600:
            print("Audio too short for reliable transcription")
            return ""

        model = _get_model()

        # Write audio to a temporary WAV file and pass the filename to faster-whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            tmp_path = Path(tf.name)
        try:
            flat = audio
            if hasattr(flat, 'flatten'):
                flat = flat.flatten()
            else:
                flat = list(flat)

            # Convert to 16-bit PCM frames
            pcm_frames = struct.pack('<' + 'h' * len(flat), *[int(max(-1.0, min(1.0, s)) * 32767) for s in flat])
            with wave.open(str(tmp_path), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm_frames)

            try:
                # Diagnostic info
                try:
                    size = tmp_path.stat().st_size
                except Exception:
                    size = None
                print(f"[DEBUG] Wrote temp WAV {tmp_path} (size={size})")

                segments, _ = model.transcribe(str(tmp_path), language="en")
            except Exception as e:
                print(f"Transcription call failed: {e}")
                traceback.print_exc()
                return ""
        finally:
            try:
                tmp_path.unlink()
            except Exception:
                pass

        # Combine all segments into single transcript
        transcript = " ".join([segment.text for segment in segments]).strip()

        if not transcript:
            print("Transcription produced empty transcript")
            return ""

        # Return lowercase for consistency
        return transcript.lower()
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
