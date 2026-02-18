"""
Overlay Display Module
Shows answers in a small, non-blocking tkinter overlay window.
Auto-dismisses after configurable duration.
"""

import tkinter as tk
import threading
import queue
import time
import config


class TkOverlayThread(threading.Thread):
    """Thread that runs a Tkinter loop and displays overlay messages from a queue."""

    def __init__(self):
        super().__init__(daemon=True)
        self.queue = queue.Queue()
        self.root = None
        self.running = True

    def run(self):
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            # Start polling loop
            self._poll_queue()
            self.root.mainloop()
        except Exception as e:
            print(f"Overlay thread error: {e}")

    def _poll_queue(self):
        try:
            while not self.queue.empty():
                text = self.queue.get_nowait()
                self._show_text(text)
        except Exception as e:
            print(f"Overlay poll error: {e}")
        finally:
            # Schedule next poll
            if self.root:
                self.root.after(200, self._poll_queue)

    def _show_text(self, text: str):
        try:
            # Create a transient Toplevel window for the overlay
            win = tk.Toplevel(self.root)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            try:
                win.attributes("-noactivate", True)
            except Exception:
                pass

            label = tk.Label(
                win,
                text=text,
                bg="#1e1e1e",
                fg="white",
                font=("Segoe UI", 10),
                wraplength=350,
                padx=10,
                pady=8,
                justify=tk.LEFT,
            )
            label.pack()

            win.update_idletasks()
            width = win.winfo_reqwidth()
            height = win.winfo_reqheight()
            screen_width = win.winfo_screenwidth()
            x = screen_width - width - 10
            y = 10
            win.geometry(f"+{x}+{y}")
            win.deiconify()

            # Auto-dismiss after configured duration
            dismiss_ms = int(config.OVERLAY_DURATION * 1000)
            win.after(dismiss_ms, win.destroy)
        except Exception as e:
            print(f"Error showing overlay: {e}")


# Start overlay thread on import
_tk_thread = TkOverlayThread()
_tk_thread.start()


def show_answer(text: str) -> None:
    """Enqueue text to be shown by the overlay thread."""
    try:
        _tk_thread.queue.put(text)
    except Exception as e:
        print(f"Failed to enqueue overlay text: {e}")
