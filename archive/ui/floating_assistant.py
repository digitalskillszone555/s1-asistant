# ui/floating_assistant.py
import tkinter as tk
from tkinter import messagebox

from ui.main_window import AssistantWindow

class FloatingBubble:
    """
    A draggable, always-on-top floating bubble for S1 Assistant.
    """
    def __init__(self):
        self.root = tk.Tk()
        
        # UI Setup for the bubble
        self.root.overrideredirect(True) # Remove title bar
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "white")
        self.root.geometry("80x80+50+50")
        self.root.configure(bg="white")

        # Initialize the chat window BEFORE we hide it, passing self.root as parent
        self.chat_window = AssistantWindow(parent=self.root)
        self.chat_window.hide()

        # Create the bubble
        self.canvas = tk.Canvas(self.root, width=70, height=70, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True)
        
        self.bubble = self.canvas.create_oval(5, 5, 65, 65, fill="#0078D7", outline="#005A9E", width=2)
        self.text = self.canvas.create_text(35, 35, text="S1", fill="white", font=("Segoe UI", 12, "bold"))

        # Bind events
        self.canvas.tag_bind(self.bubble, "<Button-1>", self._on_click)
        self.canvas.tag_bind(self.text, "<Button-1>", self._on_click)
        
        self.root.bind("<B1-Motion>", self._on_drag)
        self.root.bind("<Button-1>", self._save_position)

    def _save_position(self, event):
        self.x = event.x
        self.y = event.y

    def _on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def _on_click(self, event):
        # Toggle visibility
        if self.chat_window.root.winfo_viewable():
            self.chat_window.hide()
        else:
            self.chat_window.show()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FloatingBubble()
    app.run()
