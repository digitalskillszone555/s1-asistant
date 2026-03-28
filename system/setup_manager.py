# system/setup_manager.py
from system.config_loader import load_config, save_config, validate_config
from memory.memory_manager import get_memory_manager
from system.ai_mode_manager import get_ai_mode_manager

def is_setup_needed():
    config = load_config()
    if not config or not validate_config(config):
        return True
    return False

def run_setup():
    print("="*30)
    print("S1 Assistant - First-Time Setup")
    print("="*30)
    print("Please configure your preferences.")

    language = _get_user_choice("Choose your language", ["en", "bn", "hi"])
    ai_mode = _get_user_choice("Choose AI Mode", ["smart", "online", "offline"])
    voice_enabled_str = _get_user_choice("Enable voice interaction?", ["true", "false"])
    voice_enabled = voice_enabled_str == "true"
    api_key = input("Enter your Gemini API Key (optional): ").strip()

    config_data = {
        "language": language,
        "ai_mode": ai_mode,
        "voice_enabled": voice_enabled,
        "api_key": api_key,
        "autonomy_enabled": True,
        "theme": "dark"
    }

    if save_config(config_data):
        print("\nConfiguration saved!")
        try:
            memory_manager = get_memory_manager()
            memory_manager.save_memory("profile", "language", language)
            get_ai_mode_manager().set_ai_mode(ai_mode)
        except: pass
    else:
        print("\nError saving config.")

    print("="*30)
    print("Setup complete!")
    print("="*30)

def get_startup_tips():
    """Returns a list of helpful tips for new users."""
    return [
        "Tip: Say 'Hey S1' to activate voice mode anytime.",
        "Tip: You can say 'open chrome' or 'search kittens on youtube'.",
        "Tip: Try 'what do you remember about me?' to see your personal profile.",
        "Tip: You can undo recent actions by clicking the Undo button or saying 'undo'."
    ]

def _get_user_choice(prompt: str, options: list):
    print(f"\n{prompt}")
    options_str = " / ".join(options)
    while True:
        choice = input(f"({options_str}): ").lower().strip()
        if choice in options: return choice
        print(f"Invalid selection.")

def perform_setup_if_needed():
    if is_setup_needed():
        run_setup()
