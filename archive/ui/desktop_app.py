# ui/desktop_app.py

import customtkinter as ctk
from interface_layer.ui_controller import get_ui_controller

class S1DesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("S1 Assistant")
        self.geometry("400x550")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.ui_controller = get_ui_controller()
        self.last_displayed_reply = ""

        # --- Create Widgets ---
        
        # Top Frame for selectors
        self.selector_frame = ctk.CTkFrame(self)
        self.selector_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.selector_frame.grid_columnconfigure([0,1,2], weight=1)

        self.user_menu = ctk.CTkOptionMenu(self.selector_frame, values=[], command=self.on_user_switch)
        self.user_menu.grid(row=0, column=0, padx=5, pady=5)
        
        self.mode_menu = ctk.CTkOptionMenu(self.selector_frame, values=[], command=self.on_mode_change)
        self.mode_menu.grid(row=0, column=1, padx=5, pady=5)
        
        self.lang_menu = ctk.CTkOptionMenu(self.selector_frame, values=["English", "Bengali"], command=self.on_lang_change)
        self.lang_menu.grid(row=0, column=2, padx=5, pady=5)

        # Reply display area
        self.reply_textbox = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.reply_textbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        # Bottom Frame for input
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.command_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type your command...")
        self.command_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.command_entry.bind("<Return>", self.on_send_command)

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", width=70, command=self.on_send_command)
        self.send_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Mic button
        self.mic_button = ctk.CTkButton(self, text="Start Listening", command=self.on_mic_toggle)
        self.mic_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.is_listening = False

        # --- Initial Population & Polling ---
        self.update_dropdowns()
        self.poll_for_updates()

    def on_send_command(self, event=None):
        command = self.command_entry.get()
        if not command:
            return
        
        self.command_entry.delete(0, "end")
        self.add_text_to_display(f"You: {command}")
        
        reply, exit_flag = self.ui_controller.send_command(command)
        if reply:
            self.add_text_to_display(f"S1: {reply}")
        if exit_flag:
            self.quit() # Or just disable inputs

    def on_mic_toggle(self):
        # This is a simplified toggle, a real app might need more robust state handling
        if not self.is_listening:
            self.ui_controller.start_listening()
            self.mic_button.configure(text="Stop Listening / Go Idle")
            self.is_listening = True
        else:
            self.ui_controller.stop_listening()
            self.mic_button.configure(text="Start Listening")
            self.is_listening = False

    def on_user_switch(self, user):
        reply = self.ui_controller.switch_user(user)
        self.add_text_to_display(f"[Switched to user: {user}]")
        self.update_dropdowns() # Refresh dropdowns for new user context

    def on_mode_change(self, mode):
        reply = self.ui_controller.change_mode(mode)
        self.add_text_to_display(f"S1: {reply}")

    def on_lang_change(self, lang):
        reply = self.ui_controller.set_language(lang)
        self.add_text_to_display(f"S1: {reply}")

    def add_text_to_display(self, text):
        self.reply_textbox.configure(state="normal")
        self.reply_textbox.insert("end", f"{text}\n\n")
        self.reply_textbox.configure(state="disabled")
        self.reply_textbox.see("end")

    def update_dropdowns(self):
        # These would ideally call the UI controller, which would then call the managers
        # For simplicity, we access the managers via the controller instance here
        users = self.ui_controller.user_manager.list_users()
        modes = self.ui_controller.mode_manager.list_modes()
        
        self.user_menu.configure(values=users)
        self.user_menu.set(self.ui_controller.user_manager.current_user)
        
        self.mode_menu.configure(values=modes)
        self.mode_menu.set(self.ui_controller.mode_manager.active_mode)

    def poll_for_updates(self):
        """Periodically check for new replies from the core."""
        current_reply = self.ui_controller.get_last_reply()
        if current_reply and current_reply != self.last_displayed_reply:
            self.add_text_to_display(f"S1 (Async): {current_reply}")
            self.last_displayed_reply = current_reply
        
        # Poll every 250ms
        self.after(250, self.poll_for_updates)

if __name__ == '__main__':
    # This allows running the UI standalone for testing, but it needs the core to be running.
    app = S1DesktopApp()
    app.mainloop()
