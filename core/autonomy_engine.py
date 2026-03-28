# core/autonomy_engine.py
# S1 Assistant - Autonomy Engine (CONTROLLED & PROACTIVE)
# Focus: Proactive habit-based suggestions with cooldown.

import time
from memory.habit_tracker import get_habit_tracker

class AutonomyEngine:
    """
    Analyzes current and historical behavior to suggest next steps.
    """
    def __init__(self):
        self.habit_tracker = get_habit_tracker()
        self.suggestion_map = {
            "search_web": "Would you like me to open the top result?",
            "search_youtube": "Should I play the first video for you?",
            "create_file": "Would you like me to open the file for editing?",
            "open_app": "Do you need anything specific opened in it?",
            "close_app": "You've closed {app}. Want to open anything else?",
            "app_not_found": "Do you want me to search online to download it?"
        }
        
        # Cooldown management
        self.last_habit_suggestion_time = 0
        self.suggested_this_session = False
        self.COOLDOWN_SEC = 3600 # 1 hour cooldown for habit suggestions

    def get_suggestion(self, intent: str, entity: str, context_manager=None) -> str:
        """Returns a proactive, contextual suggestion."""
        # 1. Check for strong time-of-day habits first (only once per session/hour)
        habit_suggestion = self._check_habits()
        if habit_suggestion:
            return habit_suggestion

        if not intent:
            return None
        
        # 2. Specialized contextual suggestions (already in engine)
        if intent == "close_app" and entity:
            return f"You've closed {entity}. Do you want to open something else?"
        
        if intent == "create_file" and entity:
            return f"I've created '{entity}'. Would you like me to open it for editing?"

        # 3. Check recent behavior (already in engine)
        if context_manager:
            recent_intents = context_manager.get_recent_intents()
            if len(recent_intents) >= 2 and recent_intents[-1] == "close_app" and recent_intents[-2] == "open_app":
                last_app = context_manager.last_app
                if last_app:
                    return f"I noticed you closed {last_app} quickly. Did you want to reopen it?"

        # Fallback to map
        return self.suggestion_map.get(intent)

    def _check_habits(self):
        """Analyzes historical patterns and suggests a habit-based action."""
        # Only suggest habits if enough time has passed
        now = time.time()
        if self.suggested_this_session or (now - self.last_habit_suggestion_time < self.COOLDOWN_SEC):
            return None

        habit = self.habit_tracker.get_time_of_day_habit()
        if habit:
            self.last_habit_suggestion_time = now
            self.suggested_this_session = True # Cooldown for this session
            
            intent = habit["intent"]
            entity = habit["entity"]
            
            if intent == "open_app":
                return f"You usually open {entity} around this time. Would you like me to launch it for you?"
            elif intent == "search_youtube":
                return f"It's about time for your usual {entity} videos. Should I search for it?"
            
        return None

    def reset_session(self):
        """Called when a new session starts to reset the session-level cooldown."""
        self.suggested_this_session = False

# Global Access
_autonomy_instance = AutonomyEngine()

def get_autonomy_engine():
    return _autonomy_instance
