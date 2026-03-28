# core/decision_engine.py
# S1 Assistant - Decision Engine (SMART CONFIRMATION)
# Focus: Risk-based decision making for actions.

from security.permission_manager import get_permission_manager
from memory.habit_tracker import get_habit_tracker

class DecisionEngine:
    """
    Evaluates risk levels and decides whether to EXECUTE, ASK, or REFUSE.
    """
    def __init__(self):
        self.permission = get_permission_manager()
        self.habit_tracker = get_habit_tracker()

    def get_risk_level(self, intent: str) -> str:
        """Categorizes intent into LOW, MEDIUM, or HIGH risk."""
        high_risk = ["delete_file", "kill_process", "format_disk", "clear_memory"]
        medium_risk = ["close_app", "write_file", "create_file", "system_change"]
        
        if intent in high_risk:
            return "HIGH"
        if intent in medium_risk:
            return "MEDIUM"
        return "LOW"

    def evaluate(self, intent_data: dict) -> str:
        """
        Determines execution strategy based on risk and trust.
        """
        intent = intent_data.get("intent", "unknown")
        risk = self.get_risk_level(intent)
        user_trusted = self.habit_tracker.is_user_trusted(intent)

        # 1. High Risk always asks
        if risk == "HIGH":
            return "ASK"
        
        # 2. Medium Risk asks if not trusted
        if risk == "MEDIUM" and not user_trusted:
            return "ASK"
            
        # 3. Low Risk or Trusted Medium executes
        return "EXECUTE"

    def get_preview_text(self, intent_data: dict) -> str:
        """Generates a human-friendly preview of what will happen."""
        intent = intent_data.get("intent")
        entity = intent_data.get("entity", "it")
        
        previews = {
            "delete_file": f"I will permanently delete the file '{entity}'.",
            "close_app": f"I'm going to close '{entity}'. Make sure your work is saved!",
            "write_file": f"I will write new content to '{entity}'.",
            "kill_process": f"I will force stop the process '{entity}'.",
            "clear_memory": "I will wipe all of your personal memory and preferences."
        }
        
        return previews.get(intent, f"I will perform the action '{intent}' on '{entity}'.")

# Global Access
_decision_engine_instance = DecisionEngine()

def get_decision_engine():
    return _decision_engine_instance
