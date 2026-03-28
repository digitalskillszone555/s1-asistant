# interface_layer/interaction_manager.py
# S1 Assistant - Interaction Manager
# Focus: Handling user confirmations and follow-up decisions.

class InteractionManager:
    """
    Parses user input for confirmation (Yes/No) or simple decisions.
    """
    def __init__(self):
        self.positive = ["yes", "yeah", "yep", "ok", "okay", "sure", "karo", "ha", "thik ache", "y"]
        self.negative = ["no", "nah", "nope", "dont", "don't", "stop", "na", "bondho koro", "n"]

    def is_confirmed(self, user_input: str) -> bool:
        """Determines if user said 'yes' based on many variations."""
        text = user_input.lower().strip()
        # Check for positive words
        for p in self.positive:
            if p == text or f" {p} " in f" {text} ":
                return True
        return False

    def is_denied(self, user_input: str) -> bool:
        """Determines if user said 'no' based on many variations."""
        text = user_input.lower().strip()
        # Check for negative words
        for n in self.negative:
            if n == text or f" {n} " in f" {text} ":
                return True
        return False

    def ask_to_close(self, app_name: str) -> str:
        """Standard prompt for closing an app after a task."""
        return f"I've opened {app_name} for you. Would you like me to close it now?"

# Global Access
_interaction_instance = InteractionManager()

def get_interaction_manager():
    return _interaction_instance
