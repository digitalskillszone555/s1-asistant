# context/context_manager.py

class ContextManager:
    """
    Manages the short-term conversational context for the assistant.
    """
    def __init__(self):
        self.last_intent = None
        self.last_entity = None
        self.last_action = None
        self.last_full_command = None

    def set_context(self, intent=None, entity=None, action=None, command=None):
        """
        Sets the context after a successful interaction.
        """
        if intent:
            self.last_intent = intent
        if entity:
            self.last_entity = entity
        if action:
            self.last_action = action
        if command:
            self.last_full_command = command
        
        print(f"[CONTEXT] Set: Intent='{self.last_intent}', Entity='{self.last_entity}', Action='{self.last_action}'")

    def get_context(self):
        """
        Retrieves the last stored context.
        """
        return {
            "intent": self.last_intent,
            "entity": self.last_entity,
            "action": self.last_action,
            "command": self.last_full_command,
        }

    def clear_context(self):
        """
        Clears the current context.
        """
        self.last_intent = None
        self.last_entity = None
        self.last_action = None
        self.last_full_command = None
        print("[CONTEXT] Cleared.")

# Global instance of the context manager
S1_CONTEXT = ContextManager()

def get_context_manager():
    return S1_CONTEXT
