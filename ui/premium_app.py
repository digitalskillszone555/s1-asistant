# ui/premium_app.py
import customtkinter as ctk
import tkinter as tk
from ui.avatar import AssistantAvatar
from ui.sounds import play_sound
from interface_layer.ui_controller import get_ui_controller
from system.config_loader import load_config, save_config
from system.setup_manager import get_startup_tips
import threading
import time

class PremiumS1App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("S1 Premium Assistant")
        self.geometry("450x750")
        
        # Load Config
        self.config = load_config()
        ctk.set_appearance_mode(self.config.get("theme", "dark"))
        ctk.set_default_color_theme("blue")
        
        self.ui_controller = get_ui_controller()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Settings Overlay ---
        self.settings_frame = ctk.CTkFrame(self, fg_color=("#f9f9f9", "#1e1e1e"), corner_radius=0)
        
        # --- 1. Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.avatar = AssistantAvatar(self.header_frame, size=120, bg="#1a1a1a")
        self.avatar.pack(pady=10)
        self.status_label = ctk.CTkLabel(self.header_frame, text="S1 Assistant", font=("Segoe UI", 18, "bold"))
        self.status_label.pack()
        
        # --- 2. Chat Area ---
        self.chat_frame = ctk.CTkScrollableFrame(self, fg_color=("#ffffff", "#2b2b2b"), corner_radius=15)
        self.chat_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # --- 3. Input ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.command_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ask me anything...", height=45, corner_radius=25)
        self.command_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.command_entry.bind("<Return>", lambda e: self.on_send())
        self.mic_btn = ctk.CTkButton(self.input_frame, text="🎤", width=50, height=45, corner_radius=25, command=self.manual_listen, fg_color="#0078D7")
        self.mic_btn.grid(row=0, column=1)

        # --- Settings Button ---
        self.settings_btn = ctk.CTkButton(self, text="⚙️", width=30, height=30, corner_radius=15, fg_color="transparent", text_color=("black", "white"), command=self.toggle_settings)
        self.settings_btn.place(relx=0.05, rely=0.05, anchor="nw")

        # --- Startup Experience ---
        user_name = self.ui_controller.memory_manager.get_memory("profile", "user_name") or "there"
        msg = f"Hey {user_name}! I'm S1. Ready to help."
        self.after(800, lambda: self.add_message("S1", msg, animate=True))
        
        # Speak greeting if voice enabled
        if self.config.get("voice_enabled"):
            from voice.voice_output import get_voice_output
            self.after(1000, lambda: get_voice_output().speak(msg))
        
        # Show tips if needed (logic placeholder)
        if True: 
            self.after(3000, self.show_tips)
        
        self.poll_state()

    def show_tips(self):
        tips = get_startup_tips()
        import random
        tip = random.choice(tips)
        self.add_message("System", tip, animate=True)

    def toggle_settings(self):
        if self.settings_frame.winfo_ismapped():
            self.settings_frame.place_forget()
        else:
            self.render_settings()
            self.settings_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def render_settings(self):
        for widget in self.settings_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.settings_frame, text="Settings", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        v_var = tk.BooleanVar(value=self.config.get("voice_enabled", True))
        ctk.CTkSwitch(self.settings_frame, text="Voice Mode", variable=v_var, command=lambda: self.update_cfg("voice_enabled", v_var.get())).pack(pady=10)
        
        a_var = tk.BooleanVar(value=self.config.get("autonomy_enabled", True))
        ctk.CTkSwitch(self.settings_frame, text="Autonomy", variable=a_var, command=lambda: self.update_cfg("autonomy_enabled", a_var.get())).pack(pady=10)
        
        t_var = tk.StringVar(value=self.config.get("theme", "dark"))
        ctk.CTkOptionMenu(self.settings_frame, values=["light", "dark"], variable=t_var, command=self.update_theme).pack(pady=10)
        
        ctk.CTkButton(self.settings_frame, text="Back", command=self.toggle_settings).pack(pady=40)

    def update_cfg(self, key, val):
        self.config[key] = val
        save_config(self.config)

    def update_theme(self, val):
        self.update_cfg("theme", val)
        ctk.set_appearance_mode(val)

    def poll_state(self):
        from utils.state import AssistantState
        current_state = self.ui_controller.state_manager.get_state()
        if hasattr(self, 'last_state') and current_state != self.last_state:
            self.on_state_change(current_state)
        self.last_state = current_state
        self.after(200, self.poll_state)

    def on_state_change(self, state):
        from utils.state import AssistantState
        from core.context_manager_v2 import get_context_v2
        emotion = get_context_v2().get_emotional_trend()
        if state == AssistantState.LISTENING:
            self.avatar.set_state("LISTENING", emotion=emotion)
            self.mic_btn.configure(fg_color="#E81123", text="🔴")
        elif state == AssistantState.IDLE:
            self.avatar.set_state("IDLE", emotion=emotion)
            self.mic_btn.configure(fg_color="#0078D7", text="🎤")

    def manual_listen(self):
        from utils.state import AssistantState
        self.ui_controller.state_manager.set_state(AssistantState.LISTENING)

    def add_message(self, sender, text, animate=False):
        is_user = (sender.lower() == "you")
        is_system = (sender.lower() == "system")
        
        bubble_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        bubble_frame.pack(fill="x", pady=5)
        
        buttons = []
        if "[BUTTONS:" in text:
            btn_part = text[text.find("[BUTTONS:"):text.find("]")]
            btn_list = btn_part.replace("[BUTTONS:", "").split(",")
            buttons = [b.strip() for b in btn_list]
            text = text.replace(btn_part + "]", "").strip()

        # Visual styling
        if is_system:
            color = "transparent"
            txt_color = "gray"
            font = ("Segoe UI", 11, "italic")
        else:
            color = "#0078D7" if is_user else ("#f0f0f0", "#3e3e3e")
            txt_color = "white" if is_user or ctk.get_appearance_mode() == "Dark" else "black"
            font = ("Segoe UI", 12)
        
        msg_bubble = ctk.CTkLabel(bubble_frame, text="" if animate else text, fg_color=color, text_color=txt_color, corner_radius=15, padx=15, pady=8, wraplength=300, justify="left", font=font)
        msg_bubble.pack(side="right" if is_user else "left", padx=5)
        
        if animate: self.animate_text(msg_bubble, text)
        
        if buttons:
            btn_container = ctk.CTkFrame(bubble_frame, fg_color="transparent")
            btn_container.pack(side="left" if not is_user else "right", padx=20, pady=2)
            for b_text in buttons:
                btn = ctk.CTkButton(btn_container, text=b_text, width=60, height=25, corner_radius=10, fg_color="#4a4a4a", command=lambda t=b_text: self.send_as_user(t))
                btn.pack(side="left", padx=2)

        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def animate_text(self, label, full_text, index=0):
        if index < len(full_text):
            label.configure(text=full_text[:index+1])
            self.chat_frame._parent_canvas.yview_moveto(1.0)
            self.after(15, lambda: self.animate_text(label, full_text, index+1))

    def send_as_user(self, text):
        self.command_entry.delete(0, "end")
        self.command_entry.insert(0, text)
        self.on_send()

    def on_send(self):
        text = self.command_entry.get().strip()
        if not text: return
        self.command_entry.delete(0, "end")
        self.add_message("You", text)
        self.avatar.set_state("THINKING")
        threading.Thread(target=self._process_command, args=(text,), daemon=True).start()

    def _process_command(self, text):
        reply, _ = self.ui_controller.send_command(text)
        self.after(0, lambda: self.add_message("S1", reply, animate=True))
        self.after(0, lambda: play_sound("DONE"))

if __name__ == "__main__":
    app = PremiumS1App()
    app.mainloop()
