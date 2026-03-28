# core/context_manager_v2.py
# S1 Assistant - Context Manager V2 (EMOTIONALLY AWARE)
# Focus: Tracking interaction history and emotional trends.

class ContextManagerV2:
    """
    Maintains a history of recent interactions and emotional trends.
    """
    def __init__(self, history_limit=3):
        self.last_app = None
        self.last_intent = None
        self.history_limit = history_limit
        self.interaction_history = []
        self.emotion_history = [] # List of last emotions

    def update_context(self, app_name: str, intent: str = None, emotion: str = "neutral"):
        """Updates context and emotional history."""
        if app_name and app_name != "it":
            self.last_app = app_name
        
        if intent:
            self.last_intent = intent

        # Push to interaction history
        entry = {"app": app_name, "intent": intent, "emotion": emotion}
        self.interaction_history.append(entry)
        if len(self.interaction_history) > self.history_limit:
            self.interaction_history.pop(0)

        # Push to emotion-only history for trend analysis
        self.emotion_history.append(emotion)
        if len(self.emotion_history) > self.history_limit:
            self.emotion_history.pop(0)

        print(f"[ContextV2] Emotion Trend: {self.emotion_history}")

    def get_emotional_trend(self) -> str:
        """Returns the most frequent emotion in recent history."""
        if not self.emotion_history:
            return "neutral"
        return max(set(self.emotion_history), key=self.emotion_history.count)

    def resolve_target(self, target: str) -> str:
        if not target or target.lower() in ["it", "this", "eta", "ota"]:
            if self.last_app:
                return self.last_app
            for entry in reversed(self.interaction_history):
                app = entry.get("app")
                if app and app != "it":
                    return app
        return target

    def get_recent_intents(self):
        return [entry.get("intent") for entry in self.interaction_history if entry.get("intent")]

# Global Access
_context_v2_instance = ContextManagerV2()

def get_context_v2():
    return _context_v2_instance
