"""
Jarvis Voice Assistant
Production-ready voice assistant with offline speech recognition.
Entry point - starts all listeners and keeps the application running.
"""

import signal
import sys
import config
import listener


def main() -> None:
    """
    Start Jarvis assistant.
    Initialize configuration, start audio listener, keep running.
    """
    print("=" * 60)
    print("JARVIS VOICE ASSISTANT")
    print("=" * 60)
    print(f"\nWake word: '{config.WAKE_NAME}' (case-insensitive)")
    print(f"Whisper model: {config.WHISPER_MODEL}")
    print(f"AI backend: {config.AI_BACKEND}")
    print(f"Workspace: {config.WORKSPACE_DIR}")
    print("\n" + "=" * 60)
    print("STARTUP NOTES:")
    print("= First run will download Whisper model (~1.5GB, takes 1-2 mins)")
    print("= Make sure to set API keys in config.py:")
    print(f"  - GROQ_API_KEY (for Groq backend)")
    print(f"  - OPENROUTER_API_KEY (for fallback)")
    print("= Microphone may request permissions on first run")
    print("=" * 60 + "\n")
    
    # Start listening for middle-click
    try:
        listener.start_listener()
        print("\nTo quit: Press Ctrl+C")
        
        # Keep main thread alive. Use a simple cross-platform sleep loop
        # instead of signal.pause() which is not available on Windows.
        signal.signal(signal.SIGINT, _signal_handler)
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            _signal_handler(None, None)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        listener.stop_listener()
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


def _signal_handler(signum, frame) -> None:
    """Handle Ctrl+C gracefully."""
    print("\n\nShutting down...")
    listener.stop_listener()
    sys.exit(0)


if __name__ == "__main__":
    main()
