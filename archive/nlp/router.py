# nlp/router.py
"""
High-level NLP router that orchestrates language detection, text normalization,
and intent matching. This module provides the main public interface for the
NLP subsystem, maintaining backward compatibility.
"""
from typing import Dict, Optional, Any, List
from nlp.language_detector import get_language_detector
from nlp.normalization import get_text_normalizer
from nlp.intent_engine import get_intent_engine
from utils.logging_utils import log_event # Centralized logging

def map_intent_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    High-level function to map a raw text string to the single best intent and entity
    using the new hybrid multilingual NLP pipeline.

    :param text: Raw user input string.
    :return: A dictionary with 'intent', 'entity', and 'confidence' keys, or None if no intent is found.
    """
    if not text.strip():
        return None

    lang_detector = get_language_detector()
    normalizer = get_text_normalizer()
    intent_engine = get_intent_engine()

    # 1. Detect Language(s)
    detected_langs = lang_detector.detect(text)
    log_event("NLP_ROUTER", "Detected Language(s).", detected_langs=detected_langs)
    if not detected_langs:
        log_event("NLP_ROUTER", "No language detected.")
        return None

    # 2. Normalize Text (based on primary detected language)
    # Pass all detected languages for more comprehensive stop word removal in normalization
    normalized_text = normalizer.normalize(text, detected_langs)
    log_event("NLP_ROUTER", f"Normalized Text: '{normalized_text}'")
    if not normalized_text:
        return None

    # 3. Find Intent and Entity with Confidence (across detected languages)
    potential_matches = intent_engine.find_best_match(normalized_text, detected_langs)

    if potential_matches:
        # For backward compatibility, return only the single highest confidence match
        best_match = potential_matches[0]
        log_event("NLP_ROUTER", f"Mapped intent: '{best_match['intent']}', Entity: '{best_match['entity']}', Confidence: {best_match['confidence']:.2f}")
        return {
            "intent": best_match['intent'],
            "entity": best_match['entity'] if best_match['entity'] else normalized_text, # Fallback to normalized text as entity if none extracted
            "confidence": best_match['confidence']
        }
    
    log_event("NLP_ROUTER", "No intent mapped.")
    return None

def detect_multiple_intents(text: str) -> List[Dict[str, Any]]:
    """
    (Future-ready) Detects multiple potential intents and entities with confidence scores.
    """
    if not text.strip():
        return []

    lang_detector = get_language_detector()
    normalizer = get_text_normalizer()
    intent_engine = get_intent_engine()

    detected_langs = lang_detector.detect(text)
    if not detected_langs:
        return []
    
    normalized_text = normalizer.normalize(text, detected_langs)
    if not normalized_text:
        return []

    return intent_engine.find_best_match(normalized_text, detected_langs)
