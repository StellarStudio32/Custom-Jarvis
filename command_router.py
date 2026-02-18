"""
Command Router Module
Routes voice commands to hardcoded handlers or AI.
Hardcoded commands bypass AI for speed and to save quota.
"""

import re
import json
from word2number import w2n
import config
import ai_handler
from actions import typer, deleter, overlay


def route(transcript: str) -> dict:
    """
    Route a transcript to either hardcoded command handler or AI.
    Hardcoded commands are matched first via regex for speed.
    
    Args:
        transcript: Transcribed voice command (should have wake word already stripped)
        
    Returns:
        Dict with keys: action, params, answer (for consistency with AI responses)
    """
    
    # Simple in-memory debounce to avoid executing identical commands twice in quick succession
    if not hasattr(route, "_recent_commands"):
        route._recent_commands = {}
    import time
    now = time.time()

    # Handle "type" command
    type_match = re.match(r"type\s+(.+)", transcript, re.IGNORECASE)
    if type_match:
        text_to_type = type_match.group(1).strip()
        last = route._recent_commands.get(("type", text_to_type))
        if last and (now - last) < 1.0:
            return {"action": "type", "params": {"text": text_to_type}, "answer": f"Already typed: {text_to_type}"}
        route._recent_commands[("type", text_to_type)] = now
        # Announce via TTS, then type
        try:
            from actions import tts
            tts.speak(f"Typing {text_to_type} now")
        except Exception:
            pass
        typer.type_text(text_to_type)
        return {
            "action": "type",
            "params": {"text": text_to_type},
            "answer": f"Typed: {text_to_type}"
        }
    
    # Handle "delete N characters" command
    delete_chars_match = re.match(r"delete\s+(\w+)\s+characters?", transcript, re.IGNORECASE)
    if delete_chars_match:
        num_str = delete_chars_match.group(1).lower()
        try:
            count = _parse_number(num_str)
            last = route._recent_commands.get(("delete_chars", count))
            if last and (now - last) < 1.0:
                return {"action": "delete_chars", "params": {"count": count}, "answer": f"Already deleted {count} characters."}
            route._recent_commands[("delete_chars", count)] = now
            try:
                from actions import tts
                tts.speak(f"Deleting {count} characters now")
            except Exception:
                pass
            deleter.delete_chars(count)
            return {
                "action": "delete_chars",
                "params": {"count": count},
                "answer": f"Deleted {count} character{'s' if count != 1 else ''}."
            }
        except ValueError:
            pass  # Fall through to AI
    
    # Handle "delete N words" command
    delete_words_match = re.match(r"delete\s+(\w+)\s+words?", transcript, re.IGNORECASE)
    if delete_words_match:
        num_str = delete_words_match.group(1).lower()
        try:
            count = _parse_number(num_str)
            last = route._recent_commands.get(("delete_words", count))
            if last and (now - last) < 1.0:
                return {"action": "delete_words", "params": {"count": count}, "answer": f"Already deleted {count} words."}
            route._recent_commands[("delete_words", count)] = now
            try:
                from actions import tts
                tts.speak(f"Deleting {count} words now")
            except Exception:
                pass
            deleter.delete_words(count)
            return {
                "action": "delete_words",
                "params": {"count": count},
                "answer": f"Deleted {count} word{'s' if count != 1 else ''}."
            }
        except ValueError:
            pass  # Fall through to AI
    
    # No hardcoded match, route to AI
    return ai_handler.ask_ai(transcript)


def _parse_number(num_str: str) -> int:
    """
    Parse a number from string form (digit or word).
    
    Args:
        num_str: Number as string (e.g., "3", "three", "twenty-five")
        
    Returns:
        Parsed integer
        
    Raises:
        ValueError: If number cannot be parsed
    """
    num_str = num_str.strip().lower()
    
    # Try digit first
    try:
        return int(num_str)
    except ValueError:
        pass
    
    # Try word-to-number
    try:
        return w2n.word_to_num(num_str)
    except Exception as e:
        raise ValueError(f"Cannot parse number '{num_str}': {e}")
