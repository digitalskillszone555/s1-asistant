# ui/main_window.py
import tkinter as tk
from tkinter import scrolledtext
import threading
from core.master_brain_v7 import process_command_master_v7
from ui.voice_ui import VoiceUI

class AssistantWindow:
    """
    Main Chat Interface for S1 Assistant.
    """
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
            
        self.root.title("S1 Assistant")
        self.root.geometry("400x600")
        self.root.configure(bg="#F3F3F3")
        self.root.attributes("-topmost", True)

        # Header
        header = tk.Frame(self.root, bg="#0078D7", height=50)
        header.pack(fill="x")
        tk.Label(header, text="S1 Assistant", font=("Segoe UI", 12, "bold"), fg="white", bg="#0078D7").pack(pady=10)

        # Chat Area
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Segoe UI", 10), bg="white", state='disabled')
        self.chat_area.pack(expand=True, fill="both", padx=10, pady=10)

        # Status Bar (Voice UI)
        self.voice_ui = VoiceUI(self.root)
        self.voice_ui.pack(fill="x", side="top", padx=10)

        # Input Area
        input_frame = tk.Frame(self.root, bg="#F3F3F3")
        input_frame.pack(fill="x", side="bottom", padx=10, pady=10)

        self.input_field = tk.Entry(input_frame, font=("Segoe UI", 11), bd=0, highlightthickness=1, highlightbackground="#CCCCCC")
        self.input_field.pack(side="left", expand=True, fill="x", padx=(0, 10), ipady=5)
        self.input_field.bind("<Return>", lambda e: self.send_message())

        self.send_btn = tk.Button(input_frame, text="Send", command=self.send_message, bg="#0078D7", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15)
        self.send_btn.pack(side="right")

        self.mic_btn = tk.Button(input_frame, text="🎤", command=self.start_voice_session, bg="#666666", fg="white", font=("Segoe UI", 10), bd=0, padx=10)
        self.mic_btn.pack(side="right", padx=5)

        self.add_message("Assistant", "Hello! I'm S1. How can I help you today?")

    def add_message(self, sender, text):
        """Adds a message to the chat display."""
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: ", "bold")
        self.chat_area.insert(tk.END, f"{text}\n\n")
        self.chat_area.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def send_message(self):
        """Processes text input."""
        user_text = self.input_field.get().strip()
        if not user_text:
            return

        self.input_field.delete(0, tk.END)
        self.add_message("You", user_text)
        
        # Run execution in background thread to keep UI responsive
        threading.Thread(target=self._execute_command, args=(user_text,), daemon=True).start()

    def _execute_command(self, text):
        self.voice_ui.set_status("THINKING")
        try:
            response = process_command_master_v7(text)
            self.root.after(0, lambda: self.add_message("S1", response))
            self.voice_ui.set_status("DONE")
        except Exception as e:
            self.root.after(0, lambda: self.add_message("Error", str(e)))
            self.voice_ui.set_status("IDLE")

    def start_voice_session(self):
        """Activates voice input logic simulation."""
        self.voice_ui.set_status("LISTENING")
        self.root.after(2000, lambda: self._process_simulated_voice("open chrome"))

    def _process_simulated_voice(self, text):
        self.add_message("You (Voice)", text)
        self._execute_command(text)

    def show(self):
        self.root.deiconify()

    def hide(self):
        self.root.withdraw()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AssistantWindow()
    app.run()
