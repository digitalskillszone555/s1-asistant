# core/config.py

import os

# ... (rest of the file is the same until AI_CONFIG)

# =========================
# S1 ASSISTANT CONFIG FILE
# Phase 13: APP_MAP Restoration
# =========================

import os

# -------------------------
# Assistant Identity
# -------------------------
ASSISTANT_NAME = "S1"

# -------------------------
# Dynamic App Mapping
# -------------------------
APP_MAP = {
    "chrome": {"win": "chrome.exe", "linux": "google-chrome", "mac": "Google Chrome"},
    "calculator": {"win": "calc.exe", "linux": "gnome-calculator", "mac": "Calculator"},
    "notepad": {"win": "notepad.exe", "linux": "gedit", "mac": "TextEdit"},
    "explorer": {"win": "explorer.exe", "linux": "nautilus", "mac": "Finder"},
    "youtube": {"win": "start chrome https://youtube.com", "linux": "google-chrome https://youtube.com", "mac": "open https://youtube.com"},
}

# -------------------------
# AI Engine Configuration
# -------------------------
OFFLINE_AI_CONFIG = {
    "model": "llama3",
}

ONLINE_AI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY", None),
    "model": "gemini-1.5-flash",
}

# --- Load User-Specific API Key ---
# This dynamically injects the user's saved API key from the new config system.
try:
    import json
    user_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'user_config.json')
    if os.path.exists(user_config_path):
        with open(user_config_path, 'r') as f:
            user_config = json.load(f)
            if user_config.get("api_key"):
                ONLINE_AI_CONFIG["api_key"] = user_config["api_key"]
                print("[Config] Loaded user-provided API key.")
except Exception as e:
    print(f"[Config WARN] Could not load user API key from config: {e}")


# Daily online API call limits for different user plans
AI_RATE_LIMITS = {
    "free": 100,
    "pro": 2000
}

# ... (rest of the file is the same)
