"""
Jarvis Configuration Module
All user-facing settings exposed as module-level constants.
Workspace directory is auto-created if missing on module import.
"""

from pathlib import Path
import os

# ==================== WAKE WORD & AUDIO ====================
WAKE_NAME = "jarvis"  # Configurable wake word (case-insensitive)
# Whisper model choices: tiny, base, small, medium, large
WHISPER_MODEL = "small"

# ==================== WORKSPACE & FILES ====================
WORKSPACE_DIR = Path("~/jarvis/workspace").expanduser()

# Auto-create workspace directory if it doesn't exist
try:
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create workspace directory at {WORKSPACE_DIR}: {e}")

# ==================== AI BACKEND ====================
# Primary backend: "groq" or "openrouter"
AI_BACKEND = "groq"

# Groq Configuration (Primary)
# Load keys from environment variables for safety (do NOT commit keys to git)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# OpenRouter Configuration (Fallback)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

# ==================== TEXT-TO-SPEECH ====================
# Run `python list_voices.py` to see available voices
TTS_VOICE_INDEX = 0  # Voice index (0 is default, try 1, 2, etc.)
TTS_RATE = 140  # Words per minute (typical range: 80-200)

# ==================== UI & DISPLAY ====================
OVERLAY_DURATION = 5  # Seconds before overlay auto-dismisses

# ==================== SEARCH ====================
SEARCH_ENGINE = "duckduckgo"  # Free, no API key required


# Safety: warn if API keys are not set
if not GROQ_API_KEY and not OPENROUTER_API_KEY:
    print("⚠️ Warning: No AI API keys found in environment. AI features will be disabled until you set GROQ_API_KEY or OPENROUTER_API_KEY.")

