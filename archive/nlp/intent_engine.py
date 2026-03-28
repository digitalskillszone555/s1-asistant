# nlp/intent_engine.py
import re
from typing import Dict, Optional, Tuple, List, Any
from nlp.data import get_nlp_data

# Using a simple Levenshtein distance approximation as full fuzzywuzzy is external.
def _levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class IntentEngine:
    """
    Core engine for detecting intent and extracting entities from normalized text.
    Uses keywords, synonyms, and fuzzy matching, now supporting multiple languages.
    """
    def __init__(self):
        self.nlp_data = get_nlp_data()

    def find_best_match(self, normalized_text: str, detected_langs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Finds all matching intents and extracts entities, returning a list of
        {intent, entity, confidence} dictionaries, sorted by confidence (desc).
        Prioritizes matches from higher confidence detected languages.
        """
        potential_matches = []

        # Iterate through detected languages, prioritizing higher confidence ones
        for lang_info in detected_langs:
            lang_code = lang_info["lang"]
            lang_confidence_factor = lang_info["confidence"] # Use this to weight intent confidence
            
            if lang_code == "unknown": # Skip if language not detected
                continue

            for intent_name, definition in self.nlp_data.intent_definitions.items():
                all_triggers = []
                
                # Add keywords for the current language
                all_triggers.extend(definition["keywords"].get(lang_code, []))
                
                # Also consider keywords from other languages if text is mixed, or if this language is not strong
                if lang_code == "mixed" or (len(detected_langs) > 1 and lang_info["confidence"] < 0.8):
                    for other_lang_code, keywords_list in definition["keywords"].items():
                        if other_lang_code != lang_code:
                            all_triggers.extend(keywords_list)
                
                # Process triggers for this intent
                for trigger in set(all_triggers): # Use set to avoid processing duplicate triggers
                    confidence = 0.0
                    entity = None
                    
                    # Exact match for keyword
                    if re.search(r'\b' + re.escape(trigger) + r'\b', normalized_text):
                        confidence = 1.0 # Highest confidence for exact match
                        entity = self._extract_entity(normalized_text, trigger, detected_langs)
                    else:
                        # Fuzzy matching for keyword
                        # Use trigger length for sensitivity of fuzzy matching
                        max_allowed_distance = max(1, len(trigger) // 3) 
                        
                        # Only perform fuzzy match if the trigger is a reasonable length
                        if len(trigger) >= 3: 
                            distance = _levenshtein_distance(trigger, normalized_text)
                            if distance <= max_allowed_distance:
                                confidence = max(0.0, 0.8 * (1 - (distance / len(trigger)))) # Max 0.8 for fuzzy
                                entity = self._extract_entity(normalized_text, trigger, detected_langs)
                    
                    if confidence > 0:
                        potential_matches.append({
                            "intent": intent_name,
                            "entity": entity,
                            "confidence": confidence * lang_confidence_factor # Weight by language detection confidence
                        })

        # Sort matches by confidence in descending order, remove duplicates (same intent/entity)
        unique_matches = {}
        for match in potential_matches:
            key = (match["intent"], match["entity"])
            if key not in unique_matches or match["confidence"] > unique_matches[key]["confidence"]:
                unique_matches[key] = match
        
        sorted_matches = sorted(unique_matches.values(), key=lambda x: x["confidence"], reverse=True)
        return sorted_matches

    def _extract_entity(self, text: str, matched_trigger: str, detected_langs: List[Dict[str, Any]]) -> str:
        """
        Extracts the entity by attempting to remove the matched trigger and relevant stopwords.
        """
        entity = text.replace(matched_trigger, "").strip()
        
        # Combine stop words from all detected languages
        combined_stop_words = set()
        for lang_info in detected_langs:
            lang_code = lang_info["lang"]
            if lang_code != "unknown" and lang_code in self.nlp_data.stop_words:
                combined_stop_words.update(self.nlp_data.stop_words[lang_code])
        
        words = entity.split()
        words = [word for word in words if word not in combined_stop_words]
        
        entity = " ".join(words).strip()
        
        # Simple cleanup if entity still contains a common verb phrase
        verb_phrases = ["বল", "দাও", "কর"] # From original BanglaPack
        for phrase in verb_phrases:
            if phrase in entity:
                entity = entity.replace(phrase, "").strip()

        return entity or None

# Singleton instance
_engine_instance = None

def get_intent_engine() -> IntentEngine:
    """Provides access to the singleton IntentEngine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = IntentEngine()
    return _engine_instance
