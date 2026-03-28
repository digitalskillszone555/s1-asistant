# skills/web_actions.py
# S1 Assistant - Web Action Module
# Focus: Browser-based search and navigation.

import webbrowser
import urllib.parse

class WebActions:
    """
    Handles web-related tasks like searching and opening URLs.
    """
    def __init__(self):
        self.base_search_url = "https://www.google.com/search?q="
        self.youtube_search_url = "https://www.youtube.com/results?search_query="

    def search_google(self, query: str) -> str:
        """Performs a Google search for the given query."""
        if not query:
            return "What would you like me to search for?"
        
        encoded_query = urllib.parse.quote(query)
        url = self.base_search_url + encoded_query
        webbrowser.open(url)
        return f"Searching Google for '{query}'..."

    def search_youtube(self, query: str) -> str:
        """Performs a YouTube search for the given query."""
        if not query:
            return "What would you like me to find on YouTube?"
        
        encoded_query = urllib.parse.quote(query)
        url = self.youtube_search_url + encoded_query
        webbrowser.open(url)
        return f"Searching YouTube for '{query}'..."

    def open_url(self, url: str) -> str:
        """Opens a specific URL in the default browser."""
        if not url:
            return "Please provide a URL to open."
        
        # Basic validation/formatting
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            
        webbrowser.open(url)
        return f"Opening {url}..."

# Global Access
_web_actions_instance = WebActions()

def get_web_actions():
    return _web_actions_instance
