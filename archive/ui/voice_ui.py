# ui/voice_ui.py
import tkinter as tk

class VoiceUI:
    """
    Visual indicator for voice activity (Listening, Thinking, etc.)
    """
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#F3F3F3")
        self.label = tk.Label(self.frame, text="Idle ✅", font=("Segoe UI", 10), bg="#F3F3F3", fg="#666666")
        self.label.pack(side="left", padx=10)
        
        self.speech_preview = tk.Label(self.frame, text="", font=("Segoe UI", 9, "italic"), bg="#F3F3F3", fg="#0078D7")
        self.speech_preview.pack(side="left", padx=5)

    def set_status(self, state):
        """
        Updates the UI status indicator.
        States: LISTENING, THINKING, EXECUTING, DONE
        """
        status_map = {
            "LISTENING": ("Listening... 🎤", "#E81123"),
            "THINKING": ("Thinking... 🧠", "#0078D7"),
            "EXECUTING": ("Executing... ⚡", "#107C10"),
            "DONE": ("Done ✅", "#666666"),
            "IDLE": ("Ready ✅", "#666666")
        }
        text, color = status_map.get(state.upper(), ("Ready ✅", "#666666"))
        self.label.config(text=text, fg=color)

    def update_preview(self, text):
        """Shows real-time speech-to-text preview."""
        self.speech_preview.config(text=text)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
