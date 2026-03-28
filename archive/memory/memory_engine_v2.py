# memory/memory_engine_v2.py
import json
import os
import datetime
from collections import Counter
from typing import Dict, Any, Optional

class MemoryEngineV2:
    """
    A non-blocking, offline-first memory and intelligence layer.
    Manages user facts, preferences, and tracks habits.
    
    Data is stored in: memory/v2/{username}/
        - facts.json
        - preferences.json
        - habits.json
    """
    def __init__(self, base_path="memory/v2"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        print("[MemoryEngineV2] Initialized.")

    def _get_user_path(self, username: str) -> str:
        """Returns the directory path for a given user."""
        return os.path.join(self.base_path, username)

    def _read_user_data(self, username: str, file_type: str) -> Dict[str, Any]:
        """
        Safely reads a JSON file for a user.
        :param username: The user's name.
        :param file_type: 'facts', 'preferences', or 'habits'.
        :return: A dictionary of the user's data, or an empty dict.
        """
        user_path = self._get_user_path(username)
        file_path = os.path.join(user_path, f"{file_type}.json")
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _write_user_data(self, username: str, file_type: str, data: Dict[str, Any]):
        """
        Safely writes data to a user's JSON file.
        """
        user_path = self._get_user_path(username)
        os.makedirs(user_path, exist_ok=True)
        file_path = os.path.join(user_path, f"{file_type}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"[MemoryEngineV2 ERROR] Could not write to {file_path}: {e}")

    # --- Fact Management ---
    def save_fact(self, username: str, key: str, value: Any):
        """Saves a key-value fact for a user."""
        facts = self._read_user_data(username, "facts")
        facts[key] = {
            "value": value,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        self._write_user_data(username, "facts", facts)

    def get_fact(self, username: str, key: str) -> Optional[Any]:
        """Retrieves a fact for a user. Returns the value or None."""
        facts = self._read_user_data(username, "facts")
        return facts.get(key, {}).get("value")

    def forget_fact(self, username: str, key: str) -> bool:
        """Forgets (deletes) a fact for a user. Returns True if successful."""
        facts = self._read_user_data(username, "facts")
        if key in facts:
            del facts[key]
            self._write_user_data(username, "facts", facts)
            return True
        return False

    # --- Preference Management ---
    def save_preference(self, username: str, key: str, value: Any):
        """Saves a persistent preference for a user (e.g., language, ai_mode)."""
        preferences = self._read_user_data(username, "preferences")
        preferences[key] = value
        self._write_user_data(username, "preferences", preferences)

    def get_preference(self, username: str, key: str) -> Optional[Any]:
        """Retrieves a preference for a user."""
        preferences = self._read_user_data(username, "preferences")
        return preferences.get(key)

    # --- Habit Tracking ---
    def track_habit(self, username: str, skill_intent: str):
        """Tracks the usage of a skill/command to identify habits."""
        habits = self._read_user_data(username, "habits")
        if "command_counts" not in habits:
            habits["command_counts"] = {}
        
        habits["command_counts"][skill_intent] = habits["command_counts"].get(skill_intent, 0) + 1
        
        if "last_used" not in habits:
            habits["last_used"] = {}
        habits["last_used"][skill_intent] = datetime.datetime.utcnow().isoformat()
        
        self._write_user_data(username, "habits", habits)

    def get_top_habits(self, username: str, top_n: int = 5) -> List[tuple]:
        """Gets the most frequently used commands for a user."""
        habits = self._read_user_data(username, "habits")
        command_counts = habits.get("command_counts", {})
        counter = Counter(command_counts)
        return counter.most_common(top_n)

    # --- Profile Aggregation ---
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Retrieves an aggregated profile of all data for a given user.
        """
        profile = {
            "facts": self._read_user_data(username, "facts"),
            "preferences": self._read_user_data(username, "preferences"),
            "habits": self._read_user_data(username, "habits")
        }
        return profile

# Optional: Singleton instance for easy access from other modules
_memory_engine_v2_instance = None

def get_memory_engine_v2():
    global _memory_engine_v2_instance
    if _memory_engine_v2_instance is None:
        _memory_engine_v2_instance = MemoryEngineV2()
    return _memory_engine_v2_instance
