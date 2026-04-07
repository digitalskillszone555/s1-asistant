# nlp/languages.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Type, Tuple, Set, Optional

class BaseLanguagePack(ABC):
    """
    Abstract base class for all language packs.
    Each language pack must define its specific NLP data and rules.
    """
    @property
    @abstractmethod
    def lang_code(self) -> str:
        """The ISO 639-1 code for the language (e.g., 'en', 'bn')."""
        pass

    @property
    @abstractmethod
    def script_unicode_ranges(self) -> List[Tuple[int, int]]:
        """List of (start, end) Unicode ranges for the language's primary script."""
        pass

    @property
    @abstractmethod
    def stop_words(self) -> set:
        """A set of common stop words for the language."""
        pass

    @property
    @abstractmethod
    def synonym_map(self) -> Dict[str, str]:
        """A dictionary mapping synonyms to canonical keywords for the language."""
        pass

    @property
    @abstractmethod
    def intent_keywords(self) -> Dict[str, List[str]]:
        """
        A dictionary mapping intent names to a list of primary keywords for this language.
        Example: {"open_app": ["open", "launch"]}
        """
        pass

    # Optional: could add properties for normalization_rules, grammar_helpers, etc.

class LanguageRegistry:
    """
    A registry to manage all available language packs.
    """
    def __init__(self):
        self._packs: Dict[str, BaseLanguagePack] = {}

    def register_pack(self, pack: BaseLanguagePack):
        """Registers a language pack instance."""
        if pack.lang_code in self._packs:
            print(f"[LanguageRegistry] Warning: Language pack for '{pack.lang_code}' already registered. Overwriting.")
        self._packs[pack.lang_code] = pack
        print(f"[LanguageRegistry] Registered language pack for '{pack.lang_code}'.")

    def get_pack(self, lang_code: str) -> Optional[BaseLanguagePack]:
        """Retrieves a language pack by its code."""
        return self._packs.get(lang_code)

    def get_all_packs(self) -> List[BaseLanguagePack]:
        """Returns a list of all registered language packs."""
        return list(self._packs.values())

# Global singleton registry instance
_registry_instance: Optional[LanguageRegistry] = None

def get_language_registry() -> LanguageRegistry:
    """Provides access to the singleton LanguageRegistry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = LanguageRegistry()
        # Auto-register core language packs here
        # This will be done in data.py or a dedicated loader for modularity
    return _registry_instance
