# ai/ai_router.py
# S1 Assistant - AI Router (PRODUCTION READY)
# Focus: Intelligent hybrid routing with keyword-based online detection.

import socket
from ai.ai_engine import get_ai_engine
from user.user_manager import get_user_manager
from system.ai_mode_manager import get_ai_mode_manager

# Keywords that trigger online AI (Gemini) over local AI (Ollama)
ONLINE_COMMAND_KEYWORDS = [
    "search for", "search", "google", "find information on",
    "news", "latest headlines", "weather", "forecast",
    "youtube", "play video", "what is", "who is", "when is", 
    "where is", "define", "meaning of"
]

def _is_internet_available():
    """Checks for a live internet connection with a 2s timeout."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def is_online_command(prompt: str) -> bool:
    """Detects if a prompt likely needs real-time online data."""
    command = prompt.lower()
    return any(kw in command for kw in ONLINE_COMMAND_KEYWORDS)

def get_ai_response(prompt: str):
    """
    Unified AI routing logic.
    """
    ai_mode_manager = get_ai_mode_manager()
    ai_mode = ai_mode_manager.get_ai_mode()
    ai_engine = get_ai_engine()
    user_manager = get_user_manager()
    user_info = user_manager.get_current_user_info()

    # 1. Forced Online
    if ai_mode == "online":
        return ai_engine.generate_online_response(prompt, user_info)

    # 2. Forced Offline
    elif ai_mode == "offline":
        return ai_engine.generate_offline_response(prompt)

    # 3. Smart Hybrid
    elif ai_mode == "smart":
        has_internet = _is_internet_available()
        
        if has_internet:
            # Route keyword-matched commands directly to online AI
            if is_online_command(prompt):
                return ai_engine.generate_online_response(prompt, user_info)
            
            # Try offline first for everything else
            offline_response = ai_engine.generate_offline_response(prompt)
            if offline_response:
                return offline_response
            
            # Fallback to online if offline fails
            return ai_engine.generate_online_response(prompt, user_info)
        
        else:
            # No internet fallback
            return ai_engine.generate_offline_response(prompt)

    return None
