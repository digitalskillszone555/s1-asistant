# ui/avatar.py
import tkinter as tk
import math
import time

class AssistantAvatar(tk.Canvas):
    """
    Animated Siri-like orb for the S1 Assistant with Emotional Awareness.
    States: IDLE, LISTENING, THINKING, SPEAKING
    Emotions: HAPPY, ANGRY, SAD, CONFUSED, NEUTRAL
    """
    def __init__(self, parent, size=150, **kwargs):
        super().__init__(parent, width=size, height=size, bg=kwargs.get("bg", "#1a1a1a"), highlightthickness=0, **kwargs)
        self.size = size
        self.center = size // 2
        self.radius = size // 3
        self.state = "IDLE"
        self.emotion = "NEUTRAL"
        self.animation_step = 0
        self.color_primary = "#0078D7"
        self.color_glow = "#00BFFF"
        
        self.orb = self.create_oval(
            self.center - self.radius, self.center - self.radius,
            self.center + self.radius, self.center + self.radius,
            fill=self.color_primary, outline=self.color_glow, width=2
        )
        self.animate()

    def set_state(self, state, emotion=None):
        self.state = state.upper()
        if emotion:
            self.emotion = emotion.upper()
        
        # Adaptive Color Mapping based on Emotion
        if self.emotion == "HAPPY":
            self.color_primary = "#FFD700" # Gold/Yellow for happy
            self.color_glow = "#FFFACD"
        elif self.emotion == "ANGRY":
            self.color_primary = "#800080" # Calm Purple for angry redirection
            self.color_glow = "#E6E6FA"
        elif self.emotion == "SAD":
            self.color_primary = "#FF8C00" # Warm Orange for support
            self.color_glow = "#FFE4B5"
        elif self.emotion == "CONFUSED":
            self.color_primary = "#00CED1" # Questioning Cyan
            self.color_glow = "#AFEEEE"
        else: # Neutral
            if self.state == "LISTENING":
                self.color_primary = "#E81123"
                self.color_glow = "#FF4500"
            elif self.state == "SPEAKING":
                self.color_primary = "#107C10"
                self.color_glow = "#7FFF00"
            else:
                self.color_primary = "#0078D7"
                self.color_glow = "#00BFFF"

        self.itemconfig(self.orb, fill=self.color_primary, outline=self.color_glow)

    def animate(self):
        self.animation_step += 1
        
        # Slower animation if user is angry (calming effect)
        step_factor = 0.1 if self.emotion == "ANGRY" else 0.2
        
        if self.state == "LISTENING":
            scale = 1.0 + 0.1 * math.sin(self.animation_step * step_factor)
            new_radius = self.radius * scale
            self.coords(self.orb, 
                        self.center - new_radius, self.center - new_radius,
                        self.center + new_radius, self.center + new_radius)
            
        elif self.state == "THINKING":
            glow_width = 2 + 2 * math.sin(self.animation_step * 0.3)
            self.itemconfig(self.orb, width=glow_width)
            
        elif self.state == "SPEAKING":
            scale = 1.0 + 0.15 * abs(math.sin(self.animation_step * 0.4))
            new_radius = self.radius * scale
            self.coords(self.orb, 
                        self.center - new_radius, self.center - new_radius,
                        self.center + new_radius, self.center + new_radius)
        else:
            scale = 1.0 + 0.02 * math.sin(self.animation_step * 0.05)
            new_radius = self.radius * scale
            self.coords(self.orb, 
                        self.center - new_radius, self.center - new_radius,
                        self.center + new_radius, self.center + new_radius)

        self.after(50, self.animate)
