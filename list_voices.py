"""
List available TTS voices.
Run: python list_voices.py
"""

import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print(f"\nFound {len(voices)} voice(s):\n")
for i, voice in enumerate(voices):
    print(f"Index {i}:")
    print(f"  ID: {voice.id}")
    print(f"  Name: {getattr(voice, 'name', 'N/A')}")
    print(f"  Languages: {getattr(voice, 'languages', 'N/A')}")
    print()

print("\nTo use a voice, set in config.py:")
print("  TTS_VOICE_INDEX = 0  # or 1, 2, etc.")
print("  TTS_RATE = 140  # words per minute")
