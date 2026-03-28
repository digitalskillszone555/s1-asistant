# skills/app_resolver.py
# A smart engine to resolve application aliases to executable commands or web URLs.

import os
import shutil

class AppResolver:
    """
    Maps user-friendly application names (aliases) to specific actions,
    like running a local executable or opening a website.
    """
    def __init__(self):
        # This mapping can be expanded and customized.
        # It can check for multiple possible executables.
        self._app_mappings = {
            # Friendly Name: [ (type, value), (fallback_type, fallback_value), ... ]
            "browser": [("app", "chrome.exe"), ("app", "msedge.exe"), ("app", "firefox.exe")],
            "editor": [("app", "code.exe"), ("app", "notepad.exe")],
            "notepad": [("app", "notepad.exe")],
            "chrome": [("app", "chrome.exe")],
            "edge": [("app", "msedge.exe")],
            "firefox": [("app", "firefox.exe")],
            "vlc": [("app", "vlc.exe")],
            "calculator": [("app", "calc.exe")],
            "whatsapp": [("app", "WhatsApp.exe"), ("web", "https://web.whatsapp.com")],
            
            # Web-only aliases
            "youtube": [("web", "https://www.youtube.com")],
            "gmail": [("web", "https://mail.google.com")],
            "facebook": [("web", "https://www.facebook.com")],
        }
        print("[AppResolver] Smart App Resolver initialized.")

    def resolve(self, alias: str) -> dict:
        """
        Resolves an alias to a concrete action.
        
        :param alias: The user-friendly name for the app (e.g., "browser").
        :return: A dictionary describing the action, or None if not found.
                 e.g., {'type': 'app', 'command': 'C:\\...\\chrome.exe'}
                 e.g., {'type': 'web', 'url': 'https://www.youtube.com'}
        """
        alias = alias.lower()
        candidates = self._app_mappings.get(alias)
        
        if not candidates:
            return None

        # Find the first valid candidate
        for action_type, value in candidates:
            if action_type == "app":
                # shutil.which() searches for the executable in the system's PATH
                command_path = shutil.which(value)
                if command_path:
                    return {"type": "app", "command": command_path, "executable": value}
            elif action_type == "web":
                return {"type": "web", "url": value}
        
        return None # No valid candidate found

    def get_all_aliases(self) -> list:
        """Returns a list of all known application aliases."""
        return list(self._app_mappings.keys())

# Singleton instance
_resolver_instance = None

def get_app_resolver():
    """Provides access to the singleton AppResolver instance."""
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = AppResolver()
    return _resolver_instance
