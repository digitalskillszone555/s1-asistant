# ai/local_ai_engine.py
# This module is now deprecated.
# All logic has been moved to the unified ai/ai_engine.py module.

print("[WARN] ai/local_ai_engine.py is deprecated and should not be used directly.")

def generate_response(prompt: str):
    from ai.ai_engine import get_ai_engine
    return get_ai_engine().generate_offline_response(prompt)