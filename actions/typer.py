"""
Typing Action Module
Types text at the current cursor position using pynput.
"""

from pynput.keyboard import Controller, Key

controller = Controller()

# Debounce state to avoid accidental double-typing
_last_typed_text = None
_last_typed_time = 0
_DEBOUNCE_SECONDS = 0.6


def type_text(text: str) -> None:
    """
    Type text at the current cursor position.
    Handles single characters, full sentences, punctuation.
    
    Args:
        text: The text to type (e.g., "hello world" or "the letter a")
    """
    global _last_typed_text, _last_typed_time
    try:
        import time
        # Simple debounce: skip if same text typed very recently
        now = time.time()
        if _last_typed_text == text and (now - _last_typed_time) < _DEBOUNCE_SECONDS:
            return
        controller.type(text)
        _last_typed_text = text
        _last_typed_time = now
    except Exception as e:
        print(f"Error typing text: {e}")
