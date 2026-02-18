"""
Deletion Action Module
Deletes characters and words using pynput.
"""

from pynput.keyboard import Controller, Key

controller = Controller()


def delete_chars(count: int) -> None:
    """
    Delete N characters backward by pressing Backspace N times.
    
    Args:
        count: Number of characters to delete
    """
    try:
        for _ in range(count):
            controller.press(Key.backspace)
            controller.release(Key.backspace)
    except Exception as e:
        print(f"Error deleting characters: {e}")


def delete_words(count: int) -> None:
    """
    Delete N words backward by selecting N words and deleting.
    Uses Shift+Ctrl+Left to select words backward, then deletes.
    
    Args:
        count: Number of words to delete
    """
    try:
        for _ in range(count):
            # Select word backward: Ctrl+Shift+Left
            with controller.pressed(Key.ctrl, Key.shift):
                controller.press(Key.left)
                controller.release(Key.left)
            # Delete the selected word
            controller.press(Key.delete)
            controller.release(Key.delete)
    except Exception as e:
        print(f"Error deleting words: {e}")
