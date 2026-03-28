# system/self_healing.py
# S1 Assistant - Self Healing System
# Focus: Detect task failures and attempt logical fallbacks.

from core.action_engine import get_action_engine
import re

class SelfHealingSystem:
    """
    Tries to recover from failed actions by suggesting or executing fallbacks.
    """
    def __init__(self):
        self.action_engine = get_action_engine()

    def handle_failure(self, intent_data: dict, error_message: str) -> str:
        """
        Takes a failed intent and tries to recover.
        Returns a new response string if a fallback is found, else None.
        """
        intent = intent_data.get("intent")
        entity = intent_data.get("entity", "")

        print(f"[SelfHealing] Detected failure for '{intent}': {error_message}")

        # Fallback 1: App not found -> Search web instead
        if intent == "open_app" and "couldn't find" in error_message.lower():
            print(f"[SelfHealing] '{entity}' not installed. Falling back to web search.")
            fallback_intent = {
                "intent": "search_web",
                "entity": f"download {entity}"
            }
            res = self.action_engine.execute(fallback_intent)
            return f"I couldn't find '{entity}' on your computer, so I searched the web for it instead."

        # Fallback 2: Invalid file extension or blocked write
        if intent in ["create_file", "write_file"] and "blocked" in error_message.lower():
            # Try to safely change it to a .txt file if it was blocked due to extension
            safe_name = "s1_recovered_file.txt"
            print(f"[SelfHealing] File action blocked. Trying safe fallback: {safe_name}")
            fallback_intent = {
                "intent": intent,
                "entity": safe_name,
                "extra_data": intent_data.get("extra_data", "")
            }
            res = self.action_engine.execute(fallback_intent)
            return f"The original file action was blocked for safety. I performed the action on '{safe_name}' instead."

        return None # No healing strategy found

# Global Access
_healer_instance = SelfHealingSystem()

def get_self_healing():
    return _healer_instance
