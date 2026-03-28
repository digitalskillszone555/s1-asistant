# system/app_matcher.py
# S1 Assistant - App Matching Engine
# Focus: Fuzzy matching of user input to registry app names.

import difflib
from system.app_discovery import get_app_registry

class AppMatcher:
    """
    Fuzzy matching system to link user-friendly names to specific app paths.
    """
    def __init__(self):
        self.registry = get_app_registry() # Loads from cache automatically

    def match(self, user_input: str, cutoff=0.5):
        """
        Attempts to find the best match for the user's input in the app registry.
        """
        if not user_input:
            return None

        user_input = user_input.lower().strip()
        app_names = list(self.registry.keys())

        # 1. Exact Match Check
        if user_input in self.registry:
            return self.registry[user_input]

        # 2. Fuzzy Match Check
        # Uses difflib for similarity matching
        matches = difflib.get_close_matches(user_input, app_names, n=1, cutoff=cutoff)
        
        if matches:
            best_match_name = matches[0]
            print(f"[AppMatcher] Found fuzzy match: '{user_input}' -> '{best_match_name}'")
            return self.registry[best_match_name]

        # 3. Keyword Match Check (e.g., 'code' in 'microsoft vs code')
        for app_name in app_names:
            if user_input in app_name:
                print(f"[AppMatcher] Found keyword match: '{user_input}' in '{app_name}'")
                return self.registry[app_name]

        return None

# Global Access
_matcher_instance = AppMatcher()

def find_app_path(name: str):
    # Refresh registry on first call or manually if needed
    _matcher_instance.registry = get_app_registry()
    return _matcher_instance.match(name)

if __name__ == "__main__":
    # Test Matching
    test_cases = ["chrome", "vscode", "vs code", "notepa", "spotif"]
    print("[AppMatcher Test]")
    for tc in test_cases:
        path = find_app_path(tc)
        print(f"INPUT: {tc:10} | MATCH: {path}")
