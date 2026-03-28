# nlp/intent_engine_v2.py
# S1 Assistant - NLP Engine Version 2
# Focus: Improved intent mapping and entity extraction for multi-language support.

import os
import json
import difflib

# --- Standardized Intent Constants ---
INTENT_OPEN_APP = "open_app"
INTENT_CLOSE_APP = "close_app"
INTENT_UNKNOWN = "unknown"

# --- Global Synonym Mapping ---
# Maps keywords from various languages/slang to standard intents.
SYNONYM_MAPPING = {
    # English
    "open": INTENT_OPEN_APP,
    "start": INTENT_OPEN_APP,
    "launch": INTENT_OPEN_APP,
    "run": INTENT_OPEN_APP,
    "close": INTENT_CLOSE_APP,
    "exit": INTENT_CLOSE_APP,
    "stop": INTENT_CLOSE_APP,
    "terminate": INTENT_CLOSE_APP,
    "kill": INTENT_CLOSE_APP,
    
    # Hindi / Bengali (Phonetic / Romanized)
    "kholo": INTENT_OPEN_APP,      # Open (Hindi/Bengali)
    "chalao": INTENT_OPEN_APP,     # Run/Start (Hindi/Bengali)
    "khulun": INTENT_OPEN_APP,     # Open (Bengali Polite)
    "chalu": INTENT_OPEN_APP,      # Start (Hindi/Bengali)
    "bandh": INTENT_CLOSE_APP,     # Close (Hindi)
    "bondho": INTENT_CLOSE_APP,    # Close (Bengali)
    "hatao": INTENT_CLOSE_APP,     # Remove/Close (Hindi Slang)
}

class IntentEngineV2:
    """
    Modular NLP engine that separates command text into standardized intents and entities.
    Supports cross-language mapping by analyzing all available language packs.
    """
    def __init__(self, packs_dir="language/packs"):
        self.packs_dir = packs_dir
        self.language_data = {}
        
        # Internal mapping to standardize keys found in JSON files
        self.standard_map = {
            "open": INTENT_OPEN_APP,
            "open_app": INTENT_OPEN_APP,
            "close": INTENT_CLOSE_APP,
            "close_app": INTENT_CLOSE_APP,
            "start": INTENT_OPEN_APP,
            "launch": INTENT_OPEN_APP
        }
        
        self._load_language_packs()

    def _load_language_packs(self):
        """Loads JSON language data from the packs directory."""
        if not os.path.exists(self.packs_dir):
            print(f"[IntentV2] Warning: Packs directory '{self.packs_dir}' not found.")
            return

        for filename in os.listdir(self.packs_dir):
            if filename.endswith(".json"):
                lang_code = filename.replace(".json", "")
                try:
                    with open(os.path.join(self.packs_dir, filename), 'r', encoding='utf-8') as f:
                        self.language_data[lang_code] = json.load(f)
                except Exception as e:
                    print(f"[IntentV2 ERROR] Failed to load {filename}: {e}")

    def normalize(self, text: str) -> str:
        """Normalizes input text by cleaning noise and standardizing casing."""
        if not text:
            return ""
        
        text = text.lower().strip()
        
        # Noise reduction (words that don't contribute to intent/entity)
        noise = ["please", "assistant", "s1", "hey", "oi", "can you", "i want to", "koro", "karne", "da", "do"]
        for word in noise:
            # Match whole words only to avoid stripping parts of app names
            text = f" {text} ".replace(f" {word} ", " ").strip()
            
        return text

    def extract_intent(self, text: str) -> str:
        """Identifies the intent using keyword matching and language pack patterns."""
        words = text.split()
        
        # 1. Quick check: Direct synonym mapping
        for word in words:
            if word in SYNONYM_MAPPING:
                return SYNONYM_MAPPING[word]

        # 2. Pattern check: Look through all loaded language packs
        for lang_code, data in self.language_data.items():
            intents = data.get("intents", {})
            for intent_key, patterns in intents.items():
                std_intent = self.standard_map.get(intent_key, intent_key)
                for pattern in patterns:
                    if pattern in text:
                        return std_intent
        
        return INTENT_UNKNOWN

    def extract_entity(self, text: str, intent: str) -> str:
        """Extracts the target entity (e.g., app name) from the command."""
        if intent == INTENT_UNKNOWN:
            return None

        # 1. Dictionary-based extraction (Highest Accuracy)
        best_match = None
        highest_score = 0.0
        cutoff = 0.8

        for lang_code, data in self.language_data.items():
            apps = data.get("entities", {}).get("app", {})
            for app_id, synonyms in apps.items():
                all_candidates = [app_id] + synonyms
                for candidate in all_candidates:
                    if candidate in text:
                        return app_id
                    
                    for word in text.split():
                        score = difflib.SequenceMatcher(None, candidate, word).ratio()
                        if score > highest_score and score >= cutoff:
                            highest_score = score
                            best_match = app_id

        if best_match:
            return best_match

        # 2. Heuristic Fallback: Pick the word that isn't the primary intent keyword
        words = text.split()
        for word in words:
            # If the word is NOT a keyword for the identified intent, it's likely the entity
            if SYNONYM_MAPPING.get(word) != intent:
                # Check it's not a generic noise word or intent pattern
                # If it's a specific app like 'youtube', we want to catch it
                return word

        return None

    def process(self, raw_text: str):
        """Processes raw text and returns a structured intent/entity dictionary."""
        normalized_text = self.normalize(raw_text)
        if not normalized_text:
            return {"intent": INTENT_UNKNOWN, "entity": None}

        intent = self.extract_intent(normalized_text)
        entity = self.extract_entity(normalized_text, intent)

        return {
            "intent": intent,
            "entity": entity
        }

# --- Global Interface ---
_engine_instance = IntentEngineV2()

def get_intent_v2(text: str):
    """
    Public API for the V2 NLP Engine.
    Returns: dict { "intent": str, "entity": str }
    """
    return _engine_instance.process(text)

# --- Test Suite ---
def test_engine():
    """Runs a series of tests to verify the V2 engine's accuracy."""
    test_cases = [
        "open chrome",                      # Basic English
        "please launch notepad",            # Noise reduction
        "chrome kholo",                    # Hindi/Bengali Mix
        "youtube chalao",                   # Hindi Entity + Intent
        "বন্ধ করো ক্যালকুলেটর",             # Bengali Native
        "terminate browser",                # Synonym + Entity Synonym
        "oi s1 notepad bondho koro",        # Noise + Multi-lang Intent
    ]
    
    print("\n[V2 NLP TEST] Starting tests...")
    print("-" * 40)
    for tc in test_cases:
        result = get_intent_v2(tc)
        print(f"INPUT : {tc}")
        print(f"RESULT: {result}")
        print("-" * 40)

if __name__ == "__main__":
    test_engine()
