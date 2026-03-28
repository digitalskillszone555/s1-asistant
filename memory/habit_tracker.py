# memory/habit_tracker.py
# S1 Assistant - Habit Tracker (ENHANCED)
# Focus: Learn user habits, including time-of-day patterns.

import json
import os
import time

HABIT_FILE = "memory/user_habits.json"

class HabitTracker:
    """
    Tracks how often a user approves/denies actions and identifies time-of-day patterns.
    """
    def __init__(self):
        self.habits = {}
        self.time_patterns = {} # { "intent_entity": { "hour": count } }
        self._load_habits()

    def _load_habits(self):
        if os.path.exists(HABIT_FILE):
            try:
                with open(HABIT_FILE, "r") as f:
                    data = json.load(f)
                    self.habits = data.get("intents", {})
                    self.time_patterns = data.get("time_patterns", {})
            except Exception:
                self.habits = {}
                self.time_patterns = {}

    def _save_habits(self):
        # Apply limits to time_patterns to prevent data bloat
        # Limit to top 100 interaction keys
        MAX_PATTERNS = 100
        if len(self.time_patterns) > MAX_PATTERNS:
            # Simple removal of oldest or least frequent could be better,
            # but for now we just keep it capped.
            sorted_keys = sorted(self.time_patterns.keys())
            for k in sorted_keys[:-MAX_PATTERNS]:
                del self.time_patterns[k]

        try:
            os.makedirs(os.path.dirname(HABIT_FILE), exist_ok=True)
            with open(HABIT_FILE, "w") as f:
                json.dump({
                    "intents": self.habits,
                    "time_patterns": self.time_patterns
                }, f, indent=4)
        except Exception:
            pass

    def record_decision(self, intent: str, approved: bool, entity: str = None):
        """Records a user's decision and time-of-day for the action."""
        # 1. Intent Approval Stats
        if intent not in self.habits:
            self.habits[intent] = {"approved": 0, "denied": 0}
        
        if approved:
            self.habits[intent]["approved"] += 1
            
            # 2. Time Pattern Tracking (only for approved actions)
            if entity:
                key = f"{intent}:{entity}"
                if key not in self.time_patterns:
                    self.time_patterns[key] = {}
                
                # Record hour of the day
                current_hour = str(time.localtime().tm_hour)
                self.time_patterns[key][current_hour] = self.time_patterns[key].get(current_hour, 0) + 1
        else:
            self.habits[intent]["denied"] += 1
            
        self._save_habits()

    def get_time_of_day_habit(self):
        """
        Analyzes patterns and returns a suggestion if a strong habit is detected
        for the current hour.
        """
        current_hour = str(time.localtime().tm_hour)
        strongest_habit = None
        max_freq = 0
        
        # We define a "habit" as an action done at least 3 times at this hour
        THRESHOLD = 3
        
        for key, hours in self.time_patterns.items():
            freq = hours.get(current_hour, 0)
            if freq >= THRESHOLD and freq > max_freq:
                max_freq = freq
                strongest_habit = key

        if strongest_habit:
            # key is "intent:entity"
            intent, entity = strongest_habit.split(":", 1)
            return {"intent": intent, "entity": entity, "freq": max_freq}
            
        return None

    def is_user_trusted(self, intent: str) -> bool:
        stats = self.habits.get(intent, {"approved": 0, "denied": 0})
        total = stats["approved"] + stats["denied"]
        if total >= 3 and (stats["approved"] / total) > 0.8:
            return True
        return False

# Global Access
_habit_instance = HabitTracker()

def get_habit_tracker():
    return _habit_instance
