# ai/online_ai_engine.py
# This module is now deprecated.
# All logic has been moved to the unified ai/ai_engine.py module.

print("[WARN] ai/online_ai_engine.py is deprecated and should not be used directly.")

def generate_online_response(prompt: str):
    from ai.ai_engine import get_ai_engine
    from user.user_manager import get_user_manager
    user_info = get_user_manager().get_current_user_info()
    return get_ai_engine().generate_online_response(prompt, user_info)