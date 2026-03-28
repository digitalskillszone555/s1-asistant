# skills/web_control.py
# Skill for interacting with the web.

import webbrowser
import socket
from urllib.parse import quote_plus
from skills.base_skill import BaseSkill

class WebControlSkill(BaseSkill):
    """
    Skill for opening websites and performing web searches.
    Requires an active internet connection.
    """
    def __init__(self):
        super().__init__(
            name="Web Control Skill",
            supported_intents=[
                "open_website", "google_search", "youtube_search",
                "open_gmail", "open_facebook", "open_whatsapp_web"
            ]
        )
        self.predefined_sites = {
            "open_gmail": "https://mail.google.com",
            "open_facebook": "https://www.facebook.com",
            "open_whatsapp_web": "https://web.whatsapp.com"
        }

    def _is_internet_available(self):
        """Checks for a live internet connection."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

    def execute(self, intent: str, entity: str, **kwargs) -> str:
        if not self._is_internet_available():
            return "Sorry, you need an internet connection for web commands."

        if intent in self.predefined_sites:
            url = self.predefined_sites[intent]
            webbrowser.open(url)
            return f"Opening {intent.replace('open_', '').replace('_', ' ').title()}."
        
        elif intent == "open_website":
            # Assume entity is a valid domain and prepend https
            url = f"https://{entity}"
            webbrowser.open(url)
            return f"Opening {entity}."

        elif intent == "google_search":
            query = quote_plus(entity)
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return f"Searching Google for '{entity}'."

        elif intent == "youtube_search":
            query = quote_plus(entity)
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            return f"Searching YouTube for '{entity}'."
            
        return f"Unknown intent '{intent}' for Web Control."
