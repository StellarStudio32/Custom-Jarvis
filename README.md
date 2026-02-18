# Jarvis - Production-Ready Python Voice Assistant

A lightweight, production-ready voice assistant that listens globally for voice commands via middle-mouse-click activation. All speech processing runs **100% offline** using `faster-whisper`. Commands are routed to hardcoded handlers (for speed) or to AI backends (Groq/OpenRouter with automatic fallback).

## Features

✅ **Global Middle-Click Activation**: Press scroll wheel to record voice commands  
✅ **Offline Speech Recognition**: Uses `faster-whisper` (Whisper-small model)  
✅ **Dual AI Backend Support**: Groq (primary) + OpenRouter (fallback) with auto-retry  
✅ **Hardcoded Fast-Path Commands**: Type, delete chars/words without AI latency  
✅ **File Operations Sandboxed**: All file I/O restricted to `workspace/` directory  
✅ **Shell Command Allowlist**: Only whitelisted commands can execute  
✅ **Non-Blocking Overlay UI**: Small tkinter window shows answers (auto-dismisses)  
✅ **Multi-Platform Support**: Windows, macOS, Linux  

## Quick Start (5 Steps)

### 1. Install Python 3.10+
Ensure Python is installed. Verify with:
```bash
python --version
```

### 2. Clone & Install Dependencies
```bash
# Clone repository (or extract if you have a zip)
cd ~/Desktop/Jarvis

# Install dependencies
pip install -r requirements.txt
```

> **First-Time Note**: `faster-whisper` will download the Whisper model on first run (~1.5GB, takes 1-2 minutes). This is normal and only happens once.

### 3. Get Free API Keys

#### Groq (Primary backend - recommended)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free account)
3. Navigate to **API Keys**
4. Copy your API key

#### OpenRouter (Fallback backend)
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up (free account)
3. Navigate to **API Keys**
4. Copy your API key

### 4. Configure API Keys
Open `config.py` and paste your keys:

```python
GROQ_API_KEY = "your-groq-key-here"
OPENROUTER_API_KEY = "your-openrouter-key-here"
```

> **Security Note**: Never commit `config.py` with real keys to public repos. Use environment variables in production:
> ```python
> import os
> GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
> ```

### 5. Run Jarvis
```bash
python main.py
```

You should see:
```
============================================================
JARVIS VOICE ASSISTANT
============================================================

Wake word: 'jarvis' (case-insensitive)
Whisper model: small
AI backend: groq
Workspace: /home/user/jarvis/workspace

============================================================
STARTUP NOTES:
= First run will download Whisper model (~1.5GB, takes 1-2 mins)
= Make sure to set API keys in config.py:
  - GROQ_API_KEY (for Groq backend)
  - OPENROUTER_API_KEY (for fallback)
= Microphone may request permissions on first run
============================================================

✓ Listening for middle-click... (Press scroll wheel to activate)

To quit: Press Ctrl+C
```

## Usage Examples

### 1. **Type Something**
Press middle mouse button → "jarvis type hello world" → Text is typed at your cursor

### 2. **Delete Characters**
Press middle mouse button → "jarvis delete five characters" → 5 backspaces (supports words like "five", "ten", or digits like "3")

### 3. **Delete Words**
Press middle mouse button → "jarvis delete two words" → Deletes last 2 words

### 4. **Ask a Question** (Uses AI)
Press middle mouse button → "jarvis what is the capital of france" → Answer appears in overlay

### 5. **Web Search**
Press middle mouse button → "jarvis search for python tutorials" → Searches DuckDuckGo, summarizes result

### 6. **File Operations**
Press middle mouse button → "jarvis create file notes.txt with content hello world" → Creates file in `workspace/`

> **All commands must start with the wake word** (default: "jarvis"). Wake word is case-insensitive.

## Configuration Options (config.py)

```python
WAKE_NAME = "jarvis"                          # Your custom wake word
WHISPER_MODEL = "small"                       # tiny, base, small, medium, large
WORKSPACE_DIR = Path("~/jarvis/workspace")    # File operations sandbox
AI_BACKEND = "groq"                           # "groq" or "openrouter"
GROQ_API_KEY = ""                             # Your Groq key
GROQ_MODEL = "llama-3.1-8b-instant"           # Groq model selection
OPENROUTER_API_KEY = ""                       # Your OpenRouter key
OPENROUTER_MODEL = "mistral/mistral-7b-instruct"  # OpenRouter model
OVERLAY_DURATION = 5                          # Seconds before overlay auto-closes
SEARCH_ENGINE = "duckduckgo"                  # Free, no API key needed
```

## Hardcoded (Fast-Path) Commands

These **bypass AI entirely** for speed and to save API quota:

| Command | Example |
|---------|---------|
| Type text | "jarvis type hello world" |
| Delete characters | "jarvis delete 3 characters" or "jarvis delete five characters" |
| Delete words | "jarvis delete 2 words" |

## AI-Powered Commands

Everything else routes to the AI backend. You can:
- Ask questions: "jarvis what is 2+2?"
- Search the web: "jarvis search for python"
- Create files: "jarvis create file report.txt with content ..."
- Run commands: "jarvis run pwd" (allowlist: ls, pwd, git, echo, python, pip, open)
- Get system info: "jarvis what time is it?"
- Copy to clipboard: "jarvis copy hello to clipboard"
- And much more...

## Troubleshooting

### Microphone Not Working
**Windows**: Run Python as Administrator (right-click → Run as Administrator)  
**macOS**: Grant microphone permission: System Preferences > Security & Privacy > Microphone  
**Linux**: Install `pulseaudio` or ensure ALSA is configured  

### No Transcription Happening
1. Check microphone is not muted
2. Speak clearly after pressing middle mouse button
3. Check console for errors
4. Try adjusting speaker/mic volume

### API Key Errors
Make sure:
- You copied the **full** key from the console (no extra spaces)
- You pasted it in `config.py` between the quotes: `GROQ_API_KEY = "your-key-here"`
- The key matches the backend (Groq key in GROQ_API_KEY, not OPENROUTER_API_KEY)

### "Permission Denied" on Linux
```bash
# Install required PA dependencies
sudo apt-get install python3-dev portaudio19-dev
pip install sounddevice
```

### Slow First Run
The first run downloads the Whisper model (~1.5GB). Expect 1-2 minutes. Subsequent runs are instant.

### Overlay Doesn't Appear (Linux)
If tkinter doesn't work, install:
```bash
sudo apt-get install python3-tk
```

## Platform-Specific Notes

### Windows
- Must run as Admin for middle-click listener to work reliably
- Microphone permissions usually automatic
- No special setup needed

### macOS
- Grant microphone permission on first run (System Preferences → Security & Privacy)
- May need to explicitly allow Python in Security preferences
- Works in both native terminal and iTerm2

### Linux
- Requires `python3-tk` for overlay window
- May need `portaudio19-dev` for sounddevice
- Works with PulseAudio or ALSA
- Some desktop environments may need special focus handling

## Architecture Overview

```
main.py                   ← Entry point, starts listener
├── listener.py          → Global middle-click listener + audio recorder
├── transcriber.py       → faster-whisper (offline)
├── command_router.py    → Routes to hardcoded or AI handler
│   ├── (hardcoded)      → typer.py, deleter.py
│   └── ai_handler.py    → Groq → OpenRouter (with fallback)
├── actions/             → Modular action handlers
│   ├── typer.py         → Keyboard typing
│   ├── deleter.py       → Character/word deletion
│   ├── searcher.py      → Web search via DuckDuckGo
│   ├── file_ops.py      → Sandboxed file I/O
│   ├── shell_ops.py     → Whitelisted shell commands
│   └── overlay.py       → tkinter answer display
└── config.py            ← All user settings
```

**Key Design Decisions**:
- Listener runs in background thread (never blocks main)
- Audio is **never sent to cloud** — all transcription happens offline
- Hardcoded commands execute first (fast, no AI latency)
- AI response is always valid JSON (validates, falls back on parse error)
- All file operations strictly sandboxed to `workspace/`
- Shell commands checked against allowlist before execution

## Advanced Usage

### Custom Wake Word
Edit `config.py`:
```python
WAKE_NAME = "friday"  # Now say "friday type hello"
```

### Use Larger Whisper Model
For better accuracy on noisy audio:
```python
WHISPER_MODEL = "medium"  # or "large" (slower, more accurate)
```

### Switch to OpenRouter as Primary
```python
AI_BACKEND = "openrouter"  # Groq becomes fallback
```

### Disable Overlay (Headless Mode)
Comment out the overlay line in `listener.py`:
```python
# overlay.show_answer(answer_text)
```

### Run in Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN apt-get install -y python3-tk  # For overlay
CMD ["python", "main.py"]
```

## Limitations & Safety

✅ **What Jarvis CAN'T do** (by design):
- Execute arbitrary code (no `eval()`, no `exec()`)
- Access files outside `workspace/` directory
- Run shell commands not in the allowlist: `{ls, pwd, git, echo, python, pip, open}`
- Send audio to the cloud (runs offline)
- Access credentials or private data without explicit permission

⚠️ **Before Deploying**:
1. Review the allowed shell commands in `actions/shell_ops.py`
2. Never commit real API keys to version control
3. Use a dedicated, low-quota API key if possible
4. Test the audio listener in your specific environment
5. Adjust `OVERLAY_DURATION` if answers appear too briefly

## Known Issues

| Issue | Platform | Workaround |
|-------|----------|-----------|
| Overlay steals focus | Linux/GNOME | Use headless mode or switch to Wayland |
| Microphone permission loop | macOS | Grant permission once, then restart terminal |
| Middle-click not detected | Linux (X11) | Try Wayland session instead |
| Very slow first startup | All | Download progress appears in console, takes 1-2 min |

## Contributing & Customization

Want to add custom commands? Edit `command_router.py`:
```python
# Add in route() function before "No hardcoded match"
if "my command" in transcript:
    return {
        "action": "custom_action",
        "params": {...},
        "answer": "Done!"
    }
```

Want a new action? Add a module in `actions/`:
```python
# actions/custom.py
def my_action(param):
    return "result"
```

Then import and call from `listener.py`'s `_execute_action()`.

## License & Support

This is a standalone, open-source project. No warranty provided. For issues:
1. Check troubleshooting section above
2. Run with `-v` flag (if implemented) for verbose logs
3. Check console output for specific error messages

## Changelog

**v1.0.0** (Feb 17, 2026)
- Initial production release
- Full feature set: offline speech, hardcoded + AI commands, file/shell sandboxing
- Dual AI backend with fallback
- Non-blocking UI overlay
- Multi-platform support

---

**Happy voice commanding! 🎤**
