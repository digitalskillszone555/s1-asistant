# memory/memory_engine.py
# S1 Assistant - Memory Intelligence Engine (ENHANCED)
# Focus: Identity memory, tagging, and contextual recall.

from memory.memory_manager import get_memory_manager
import time

class MemoryEngine:
    """
    Higher-level logic for managing and recalling personal information.
    """
    def __init__(self):
        self.memory_manager = get_memory_manager()
        self.categories = ["habit", "preference", "info", "identity"]

    def analyze_and_memorize(self, text: str, intent_data: dict):
        """
        Passive analysis of text to find personal details or preferences.
        """
        text_lower = text.lower()
        
        # 1. Identity Detection (Name)
        if "my name is " in text_lower or "call me " in text_lower:
            words = text.split()
            # Simplistic name extraction: word after 'is' or 'me'
            try:
                name = words[-1].strip("?.!")
                self.save_identity("user_name", name)
                print(f"[MemEngine] Passive identity saved: user_name = {name}")
            except IndexError: pass

        # 2. Preference Detection
        elif "i like " in text_lower or "i prefer " in text_lower:
            self.save_preference("interest", text)
            print(f"[MemEngine] Passive preference saved.")

    def save_identity(self, key: str, value: str):
        """Saves core identity traits (name, role)."""
        self.memory_manager.save_memory("profile", key, value)

    def save_preference(self, key: str, value: str):
        """Saves user preferences with auto-tagging."""
        # We store them in 'facts' with a specific prefix/tag for now
        tag = "PREFERENCE"
        self.memory_manager.save_memory("facts", f"{tag}:{key}", value)

    def save_explicit_fact(self, fact_to_remember: str):
        """Saves a fact with basic categorization."""
        if not fact_to_remember:
            return False, "There was nothing to remember."
        
        # Simple tagging logic
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
        Example: If opening an app, check if we know any preference about it.
        """
        # This is used by MasterBrainV7 to inject personality
        if current_intent == "greeting":
            user_name = self.memory_manager.get_memory("profile", "user_name")
            if user_name:
                return f"Your name is {user_name}, right? Good to see you again!"
        
        if current_intent == "open_app" and entity:
            # Check if we have a preference or habit related to this app
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
