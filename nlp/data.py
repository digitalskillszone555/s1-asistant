# nlp/data.py
"""
Centralized, dynamically loaded data store for all NLP intent definitions
and language-specific data, aggregated from registered language packs.
"""
from typing import Dict, List, Any, Set, Tuple, Optional
from nlp.languages import get_language_registry, BaseLanguagePack

# --- Import concrete language packs to register them ---
# This ensures that these packs are loaded and registered with the LanguageRegistry.
from nlp.packs.english_pack import EnglishPack
from nlp.packs.bangla_pack import BanglaPack

class NLPData:
    def __init__(self):
        self._language_registry = get_language_registry()
        self._register_default_packs()
        self.stop_words: Dict[str, Set[str]] = {}
        self.intent_definitions: Dict[str, Dict[str, Any]] = {}
        self._load_all_data()

    def _register_default_packs(self):
        """Registers the default language packs (English and Bangla)."""
        self._language_registry.register_pack(EnglishPack())
        self._language_registry.register_pack(BanglaPack())

    def _load_all_data(self):
        """Aggregates data from all registered language packs."""
        unified_intent_definitions = {}
        unified_stop_words = {}

        for pack in self._language_registry.get_all_packs():
            # Aggregate stop words
            unified_stop_words[pack.lang_code] = pack.stop_words

            # Aggregate intent definitions
            for intent_name, keywords_for_lang in pack.intent_keywords.items():
                if intent_name not in unified_intent_definitions:
                    unified_intent_definitions[intent_name] = {"keywords": {}, "synonyms": {}}
                
                # Add language-specific keywords
                unified_intent_definitions[intent_name]["keywords"][pack.lang_code] = keywords_for_lang
                
                # Add language-specific synonyms
                if hasattr(pack, 'synonym_map'):
                    unified_intent_definitions[intent_name]["synonyms"][pack.lang_code] = pack.synonym_map
        
        self.stop_words = unified_stop_words
        self.intent_definitions = unified_intent_definitions

# Singleton instance of NLPData
_nlp_data_instance: Optional[NLPData] = None

def get_nlp_data() -> NLPData:
    """Provides access to the singleton NLPData instance."""
    global _nlp_data_instance
    if _nlp_data_instance is None:
        _nlp_data_instance = NLPData()
    return _nlp_data_instance

# --- Convenience access for other modules ---
# Other modules can import these directly after calling get_nlp_data() once.
# This ensures dynamic loading is handled.
STOP_WORDS = get_nlp_data().stop_words
INTENT_DEFINITIONS = get_nlp_data().intent_definitions
