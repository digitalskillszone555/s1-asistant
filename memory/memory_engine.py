# memory/memory_engine.py
# S1 Assistant - Memory Intelligence Engine (ENHANCED)
# Focus: Identity memory, tagging, and contextual recall.

from memory.memory_manager import get_memory_manager
from memory.habit_tracker import get_habit_tracker
import time
import json
import os

class MemoryEngine:
    """
    Higher-level logic for managing and recalling personal information.
    """
    def __init__(self):
        self.memory_manager = get_memory_manager()
        self.habit_tracker = get_habit_tracker()
        self.categories = ["habit", "preference", "info", "identity"]
        
        # Caching logic
        self._cache = {}
        self._cache_time = 0
        self._cache_ttl = 30 # 30 seconds

    def _get_cached_data(self, key):
        if time.time() - self._cache_time > self._cache_ttl:
            self._cache = {} # Invalidate
            return None
        return self._cache.get(key)

    def _set_cached_data(self, key, value):
        self._cache[key] = value
        self._cache_time = time.time()

    def analyze_and_memorize(self, text: str, intent_data: dict):
        """
        Passive analysis of text to find personal details or preferences.
        """
        text_lower = text.lower()
        
        # 1. Identity Detection (Name)
        if "my name is " in text_lower or "call me " in text_lower:
            words = text.split()
            try:
                name = words[-1].strip("?.!")
                self.save_identity("user_name", name)
                print(f"[MemEngine] Passive identity saved: user_name = {name}")
            except IndexError: pass

        # 2. Preference Detection
        elif "i like " in text_lower or "i prefer " in text_lower:
            self.save_preference("interest", text)
            print(f"[MemEngine] Passive preference saved.")

    def get_frequent_apps(self):
        """Returns most used apps based on habit tracker (threshold >= 3)."""
        cached = self._get_cached_data("frequent_apps")
        if cached: return cached

        habit_tracker = get_habit_tracker()
        patterns = habit_tracker.time_patterns
        
        apps = {}
        for key, hours in patterns.items():
            if key.startswith("open_app:"):
                app_name = key.split(":", 1)[1]
                total_uses = sum(hours.values())
                if total_uses >= 3:
                    apps[app_name] = total_uses
        
        sorted_apps = sorted(apps.items(), key=lambda x: x[1], reverse=True)
        result = [app for app, count in sorted_apps]
        self._set_cached_data("frequent_apps", result)
        return result

    def get_time_based_habits(self):
        """Detects patterns (morning = chrome, night = youtube) based on threshold >= 3."""
        cached = self._get_cached_data("time_based_habits")
        if cached: return cached

        habit_tracker = get_habit_tracker()
        patterns = habit_tracker.time_patterns
        
        habits = []
        for key, hours in patterns.items():
            if key.startswith("open_app:"):
                app_name = key.split(":", 1)[1]
                for hour_str, count in hours.items():
                    if count >= 3:
                        hour = int(hour_str)
                        time_of_day = self._get_time_of_day(hour)
                        habits.append(f"{time_of_day} = {app_name}")
        
        self._set_cached_data("time_based_habits", habits)
        return habits

    def _get_time_of_day(self, hour: int) -> str:
        if 6 <= hour < 12: return "morning"
        elif 12 <= hour < 17: return "afternoon"
        elif 17 <= hour < 22: return "evening"
        else: return "night"

    def get_user_profile_summary(self):
        """Returns short summary: 'User likes Chrome, works in morning, uses Notion often'."""
        cached = self._get_cached_data("profile_summary")
        if cached: return cached

        frequent_apps = self.get_frequent_apps()
        time_habits = self.get_time_based_habits()
        
        profile = self.memory_manager._load_memory("profile") or {}
        name = profile.get("user_name", {}).get("value", "User")

        parts = [f"User is {name}"]
        if frequent_apps:
            parts.append(f"frequently uses {', '.join(frequent_apps[:3])}")
        if time_habits:
            parts.append(f"patterns detected: {', '.join(time_habits[:3])}")
            
        summary = ". ".join(parts)
        self._set_cached_data("profile_summary", summary)
        return summary

    def save_identity(self, key: str, value: str):
        """Saves core identity traits (name, role)."""
        self.memory_manager.save_memory("profile", key, value)

    def save_preference(self, key: str, value: str):
        """Saves user preferences with auto-tagging."""
        tag = "PREFERENCE"
        self.memory_manager.save_memory("facts", f"{tag}:{key}", value)

    def save_explicit_fact(self, fact_to_remember: str):
        """Saves a fact with basic categorization."""
        if not fact_to_remember:
            return False, "There was nothing to remember."
        
        category = "info"
        if any(w in fact_to_remember.lower() for w in ["like", "prefer", "love", "hate"]):
            category = "preference"
        elif any(w in fact_to_remember.lower() for w in ["usually", "always", "every day"]):
            category = "habit"

        key = f"FACT:{category}:{int(time.time())}"
        self.memory_manager.save_memory("facts", key, fact_to_remember)
        return True, f"Alright, I've noted that as a {category}."

    def recall_for_context(self, current_intent: str, entity: str = None) -> str:
        """
        Provides a 'Did you know' or 'Recall' snippet for the brain.
        """
        if current_intent == "greeting":
            user_name = self.memory_manager.get_memory("profile", "user_name")
            if user_name:
                return f"Your name is {user_name}, right? Good to see you again!"
        
        if current_intent == "open_app" and entity:
            facts = self.memory_manager.list_memory("facts")
            for f in facts:
                if entity.lower() in f.lower():
                    return f"I remember you mentioned: '{f}'. Should I apply that context?"
                    
        return None

    def get_memory_summary(self):
        """Comprehensive summary of everything remembered about the user."""
        profile = self.memory_manager._load_memory("profile") or {}
        facts = self.memory_manager._load_memory("facts") or {}
        
        summary = []
        
        # 1. Identity
        name = profile.get("user_name", {}).get("value")
        if name: summary.append(f"I know your name is {name}.")
        
        # 2. Categorized Facts
        categorized = {"preference": [], "habit": [], "info": []}
        for key, entry in facts.items():
            val = entry.get("value", "")
            if "preference" in key.lower(): categorized["preference"].append(val)
            elif "habit" in key.lower(): categorized["habit"].append(val)
            else: categorized["info"].append(val)
            
        if categorized["preference"]:
            summary.append(f"Preferences: {', '.join(categorized['preference'][:3])}")
        if categorized["habit"]:
            summary.append(f"Habits: {', '.join(categorized['habit'][:3])}")
        if categorized["info"]:
            summary.append(f"General info: {', '.join(categorized['info'][:3])}")
            
        return "\n".join(summary) if summary else "I don't remember anything personal about you yet."

    def forget_last_fact(self):
        """Forgets the most recently added fact or preference."""
        all_facts = self.memory_manager._load_memory("facts")
        if not all_facts:
            return False, "Nothing left to forget!"
            
        last_key = max(all_facts, key=lambda k: all_facts[k].get('timestamp', 0))
        self.memory_manager.delete_memory("facts", last_key)
        return True, "Done. I've forgotten that."

    def clear_all_memory(self):
        """Safety cleared all personal data."""
        self.memory_manager._save_memory("facts", {})
        self.memory_manager._save_memory("profile", {})
        return True, "Memory wiped clean."

# Global instance
S1_MEMORY_ENGINE = MemoryEngine()

def get_memory_engine():
    return S1_MEMORY_ENGINE
