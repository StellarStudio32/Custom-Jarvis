"""
Audio Listener Module
Listens for middle mouse button (scroll wheel), records audio on press, transcribes on release.
Runs in background thread without blocking main process.
"""

import threading
import sounddevice as sd
from pynput import mouse
import config
import transcriber
import command_router
from actions import overlay


class AudioListener:
    """Listens for middle-click and records audio."""
    
    def __init__(self):
        self.is_recording = False
        self.audio_buffer = []
        self.mouse_listener = None
        self.sample_rate = 16000  # Whisper expects 16kHz
    
    def start(self) -> None:
        """Start listening for middle-click events."""
        self.mouse_listener = mouse.Listener(
            on_click=self._on_click
        )
        self.mouse_listener.start()
        print("✓ Listening for middle-click... (Press scroll wheel to activate)")
    
    def stop(self) -> None:
        """Stop listening for events."""
        if self.mouse_listener:
            self.mouse_listener.stop()
    
    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """
        Handle mouse click events.
        Start recording on middle button press, process on release.
        """
        if button != mouse.Button.middle:
            return
        
        if pressed:
            # Middle button pressed: start recording
            self._start_recording()
        else:
            # Middle button released: stop and process
            self._stop_and_process()
    
    def _start_recording(self) -> None:
        """Start recording audio in background thread."""
        if not self.is_recording:
            self.is_recording = True
            self.audio_buffer = []
            print("[REC]", end=" ", flush=True)
            
            # Start recording in dedicated thread
            threading.Thread(target=self._record_audio, daemon=True).start()
    
    def _record_audio(self) -> None:
        """Record audio until is_recording is False."""
        try:
            with sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                dtype='float32',
                blocksize=1024
            ) as stream:
                while self.is_recording:
                    data, _ = stream.read(1024)
                    self.audio_buffer.append(data)
        except Exception as e:
            print(f"\nMicrophone error: {e}")
            self.is_recording = False
    
    def _stop_and_process(self) -> None:
        """Stop recording and process audio."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        print("[END]")
        
        if not self.audio_buffer:
            print("No audio captured")
            return
        
        # Concatenate audio chunks
        try:
            # Flatten all audio chunks into a single buffer
            audio_data = []
            for chunk in self.audio_buffer:
                if hasattr(chunk, 'flatten'):
                    audio_data.extend(chunk.flatten())
                else:
                    audio_data.extend(chunk)
        except Exception as e:
            print(f"Error processing audio: {e}")
            return
        
        # Process in background thread to avoid blocking
        threading.Thread(
            target=self._transcribe_and_route,
            args=(audio_data, self.sample_rate),
            daemon=True
        ).start()
    
    def _transcribe_and_route(self, audio_data, sample_rate: int) -> None:
        """
        Transcribe audio and route command.
        Runs in background thread.
        """
        try:
            # Transcribe
            transcript = transcriber.transcribe(audio_data, sample_rate=sample_rate)
            if not transcript:
                print("Transcription failed or produced empty result")
                return
            
            print(f"Transcript: {transcript}")
            
            # Check for wake word (allow punctuation like commas after the wake word)
            import re
            pattern = rf"^\s*{re.escape(config.WAKE_NAME)}\b[\s,:-]*?(.*)$"
            m = re.match(pattern, transcript, re.IGNORECASE)
            if not m:
                print(f"No wake word detected (looking for: {config.WAKE_NAME})")
                return
            # Extract command after wake word and sanitize leading punctuation/whitespace
            command = m.group(1)
            # Remove leading non-word characters (commas, punctuation, etc.) and surrounding whitespace
            command = re.sub(r"^[\s\W_]+", "", command).strip()
            if not command:
                print("No command after wake word")
                return
            
            print(f"Command: {command}")
            
            # Route command
            result = command_router.route(command)
            
            # Execute action based on result
            self._execute_action(result)
            
            # Show answer overlay
            answer_text = result.get("answer", "Done")
            overlay.show_answer(answer_text)
        
        except Exception as e:
            print(f"Error processing command: {e}")
            overlay.show_answer(f"Error: {str(e)}")
    
    def _execute_action(self, action_dict: dict) -> None:
        """
        Execute the action from the AI response or hardcoded handler.
        
        Args:
            action_dict: Dict with keys: action, params, answer
        """
        try:
            action = action_dict.get("action", "respond")
            params = action_dict.get("params", {})
            
            # Hardcoded actions are already executed by command_router
            # So we only handle AI-returned actions here
            
            if action == "web_search":
                from actions import searcher
                query = params.get("query", "")
                if query:
                    result = searcher.web_search(query)
                    print(f"Search result: {result}")
            
            elif action == "watch_youtube":
                from actions import youtube
                query = params.get("query", "")
                if query:
                    youtube.watch_youtube(query)
            
            elif action == "open_app":
                from actions import shell_ops
                app_name = params.get("name", "")
                if app_name:
                    try:
                        shell_ops.run_command(f"open {app_name}")
                    except Exception:
                        print(f"Could not open app: {app_name}")
            
            elif action == "create_file":
                from actions import file_ops
                filename = params.get("name", "")
                content = params.get("content", "")
                if filename:
                    file_ops.create_file(filename, content)
            
            elif action == "read_file":
                from actions import file_ops
                filename = params.get("name", "")
                if filename:
                    content = file_ops.read_file(filename)
                    print(f"File content: {content}")
            
            elif action == "run_command":
                from actions import shell_ops
                cmd = params.get("cmd", "")
                if cmd:
                    output = shell_ops.run_command(cmd)
                    print(f"Command output: {output}")
            
            elif action == "clipboard_write":
                import pyperclip
                text = params.get("text", "")
                if text:
                    pyperclip.copy(text)
            
            elif action == "clipboard_read":
                import pyperclip
                content = pyperclip.paste()
                print(f"Clipboard: {content}")
            
            elif action == "system_info":
                import platform
                import psutil
                import datetime
                metric = params.get("metric", "time")
                if metric == "time":
                    info = str(datetime.datetime.now().strftime("%H:%M:%S"))
                elif metric == "battery":
                    try:
                        info = f"{psutil.sensors_battery().percent}%"
                    except Exception:
                        info = "Battery info unavailable"
                elif metric == "disk":
                    info = f"{psutil.disk_usage('/').percent}% used"
                else:
                    info = "Unknown metric"
                print(f"System info: {info}")
            
            elif action == "respond":
                # Just show the answer (already handled by overlay)
                pass
        
        except Exception as e:
            print(f"Error executing action: {e}")


# Global listener instance
_listener = AudioListener()


def start_listener() -> None:
    """Start the global audio listener."""
    _listener.start()


def stop_listener() -> None:
    """Stop the global audio listener."""
    _listener.stop()
