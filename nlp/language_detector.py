# nlp/language_detector.py
import re
from typing import Literal, Dict, List, Tuple, Any
from nlp.data import get_nlp_data # Import the NLPData instance to get dynamic STOP_WORDS
from nlp.languages import get_language_registry # Import language registry

class LanguageDetector:
    """
    Detects the primary language(s) of the input text (English, Bangla, Mixed, or Unknown)
    using heuristics, character ranges, and stop words from registered language packs.
    Returns an ordered list of detected languages with confidence scores.
    """
    def __init__(self):
        self.nlp_data = get_nlp_data()
        self.language_registry = get_language_registry()

    def _count_script_chars(self, text: str) -> Dict[str, int]:
        """Counts characters within specific script ranges for all registered languages."""
        counts: Dict[str, int] = {pack.lang_code: 0 for pack in self.language_registry.get_all_packs()}
        counts["other"] = 0
        
        for char in text:
            char_code = ord(char)
            found_script = False
            for pack in self.language_registry.get_all_packs():
                for start, end in pack.script_unicode_ranges:
                    if start <= char_code <= end:
                        counts[pack.lang_code] += 1
                        found_script = True
                        break
                if found_script:
                    break
            if not found_script and not char.isspace() and not char.isdigit():
                counts["other"] += 1
        return counts

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Detects the language(s) of the input text, returning a list of
        {lang: str, confidence: float} dictionaries, sorted by confidence.
        """
        if not text.strip():
            return []

        lower_text = text.lower()
        script_counts = self._count_script_chars(text)
        
        detected_languages = []
        total_script_chars = sum(count for lang_code, count in script_counts.items() if lang_code != "other")

        # Heuristic 1: Based on dominant script
        if total_script_chars > 0:
            for pack in self.language_registry.get_all_packs():
                lang_code = pack.lang_code
                if script_counts[lang_code] > 0:
                    script_ratio = script_counts[lang_code] / total_script_chars
                    # Assign higher confidence if script is dominant
                    if script_ratio > 0.7: 
                        detected_languages.append({"lang": lang_code, "confidence": script_ratio * 0.9 + 0.1}) # Boost confidence
                    elif script_ratio > 0.1: # Minor presence
                        detected_languages.append({"lang": lang_code, "confidence": script_ratio * 0.5})


        # Heuristic 2: Fallback/refinement using stop word detection
        for pack in self.language_registry.get_all_packs():
            lang_code = pack.lang_code
            stop_word_count = sum(1 for word in lower_text.split() if word in pack.stop_words)
            if stop_word_count > 0:
                # Add or update confidence based on stop words
                current_confidence = next((item["confidence"] for item in detected_languages if item["lang"] == lang_code), 0.0)
                # Max stop word count could be ~text_length / 2, so scale accordingly
                stop_word_confidence = min(1.0, stop_word_count / len(lower_text.split()) * 0.5) if len(lower_text.split()) > 0 else 0
                
                # Combine script and stop word confidence
                combined_confidence = max(current_confidence, stop_word_confidence)
                
                # Update existing entry or add new one
                if not any(item["lang"] == lang_code for item in detected_languages):
                    detected_languages.append({"lang": lang_code, "confidence": combined_confidence})
                else:
                    for item in detected_languages:
                        if item["lang"] == lang_code:
                            item["confidence"] = max(item["confidence"], combined_confidence)
                            break
        
        # Sort by confidence descending
        detected_languages.sort(key=lambda x: x["confidence"], reverse=True)

        # Ensure confidence does not exceed 1.0
        for item in detected_languages:
            item["confidence"] = min(1.0, item["confidence"])

        # Handle mixed or unknown scenarios
        if len(detected_languages) > 1 and detected_languages[0]["confidence"] < 0.8:
            # If multiple languages detected with no clear dominant one, mark as mixed.
            # This is a simplification; a truly "mixed" entry might need to be explicitly added.
            # For now, we return the list. The intent engine will handle multi-language triggers.
            pass 
        elif not detected_languages:
            return [{"lang": "unknown", "confidence": 1.0}] # Return unknown if nothing detected
        
        return detected_languages

# Singleton instance
_detector_instance = None

def get_language_detector() -> LanguageDetector:
    """Provides access to the singleton LanguageDetector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = LanguageDetector()
    return _detector_instance
