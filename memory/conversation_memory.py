# memory/conversation_memory.py
# S1 Assistant - Conversation Memory
# Focus: Maintaining a short-term history of interactions and context.

class ConversationMemory:
    """
    Stores a rolling window of recent user-assistant turns.
    Helps in resolving follow-ups and maintaining context.
    """
    def __init__(self, max_history=10):
        self.history = [] # List of { "user": str, "assistant": str, "intent": str, "entity": str }
        self.max_history = max_history
        self.context = {
            "last_app": None,
            "last_entity": None,
            "last_intent": None,
            "topic": None
        }

    def add_turn(self, user_text: str, assistant_text: str, intent_data: dict = None):
        """Adds a conversation turn and updates context."""
        turn = {
            "user": user_text,
            "assistant": assistant_text,
            "intent_data": intent_data
        }
        self.history.append(turn)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        if intent_data:
            intent = intent_data.get("intent")
            entity = intent_data.get("entity")
            
            if intent and intent != "unknown":
                self.context["last_intent"] = intent
            
            if entity:
                self.context["last_entity"] = entity
                if intent == "open_app":
                    self.context["last_app"] = entity

    def get_last_app(self):
        return self.context.get("last_app")

    def get_last_intent(self):
        return self.context.get("last_intent")

# Global Access
_conv_memory_instance = ConversationMemory()

def get_conversation_memory():
    return _conv_memory_instance
