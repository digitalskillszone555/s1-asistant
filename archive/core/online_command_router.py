# core/online_command_router.py

from ai.ai_engine import get_ai_engine
from user.user_manager import get_user_manager

# List of keywords that indicate a command requires online access.
# This list is intentionally specific to avoid routing local commands online.
ONLINE_COMMAND_KEYWORDS = [
    "search for", "search", "google", "find information on",
    "news", "latest headlines",
    "weather", "forecast",
    "youtube", "play video",
    "what is", "who is", "when is", "where is", # General knowledge questions
    "define", "meaning of"
]

def is_online_command(prompt: str) -> bool:
    """
    Checks if a command prompt likely requires an online connection.
    It does this by checking for the presence of specific keywords.
    This is a crucial part of the hybrid AI strategy, ensuring that offline-capable
    commands are handled locally first.
    """
    command = prompt.lower()
    return any(keyword in command for keyword in ONLINE_COMMAND_KEYWORDS)

def route_online_command(prompt: str):
    """
    If a command is identified as an online command, this function routes it
    directly to the online AI engine.
    """
    print(f"[Online Command Router] Routing '{prompt}' to online AI engine.")
    ai_engine = get_ai_engine()
    user_manager = get_user_manager()
    user_info = user_manager.get_current_user_info()
    return ai_engine.generate_online_response(prompt, user_info)