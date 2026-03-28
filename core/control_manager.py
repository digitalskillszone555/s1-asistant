# core/control_manager.py
# S1 Assistant - Control Manager
# Focus: Orchestrating post-task logic and user decisions.

from core.task_completion import check_task_completion
from interface_layer.interaction_manager import get_interaction_manager
from core.action_engine import get_action_engine

class ControlManager:
    """
    Decides the next steps based on task outcome and user input.
    """
    def __init__(self):
        self.interaction = get_interaction_manager()
        self.action_engine = get_action_engine()
        self.pending_decisions = {} # { "session_id": intent_data }

    def handle_task_result(self, intent_data: dict, result_message: str, session_id="default"):
        """
        Processes a task result and decides if a follow-up question is needed.
        """
        outcome = check_task_completion(intent_data, result_message)
        
        # If an app was opened, we might want to ask to close it later
        if outcome["status"] == "running" and intent_data.get("intent") == "open_app":
            self.pending_decisions[session_id] = intent_data
            return f"{result_message} (Keep it open?)"

        return result_message

    def handle_user_feedback(self, user_input: str, session_id="default") -> str:
        """
        Handles the user's response to a follow-up question.
        """
        if session_id not in self.pending_decisions:
            return None # Not waiting for any decision

        intent_data = self.pending_decisions.pop(session_id)
        
        if self.interaction.is_denied(user_input):
            # User wants to close it
            close_intent = {
                "intent": "close_app",
                "entity": intent_data.get("entity")
            }
            return self.action_engine.execute(close_intent)
        
        elif self.interaction.is_confirmed(user_input):
            # User wants to keep it
            return f"Okay, I'll leave {intent_data.get('entity')} running."

        return None

# Global Access
_control_instance = ControlManager()

def get_control_manager():
    return _control_instance
