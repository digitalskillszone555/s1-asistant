# nlp/control_intent.py
# S1 Assistant - Natural Control Parser
# Focus: Detecting control intents from natural language (En/Bn/Banglish).

import re

class ControlIntentParser:
    """
    Parses natural language specifically for app control and task management.
    """
    def __init__(self):
        # Intent patterns for multi-language support
        self.patterns = {
            "close_app": [
                r"close", r"stop", r"exit", r"terminate", r"kill",
                r"বন্ধ করো", r"বন্ধ কর", r"বন্ধ করে দাও",
                r"kete dao", r"bondho koro", r"bondho kor", r"lagbe na", r"close it", r"stop it"
            ],
            "minimize_app": [
                r"minimize", r"hide", r"choto koro", r"sariye dao"
            ],
            "switch_app": [
                r"switch to", r"go to", r"focus on", r"niye cholo"
            ]
        }

    def detect_intent(self, text: str) -> str:
        """Detects the control intent from raw text."""
        text = text.lower().strip()
        
        for intent, regexes in self.patterns.items():
            for regex in regexes:
                if re.search(r"\b" + re.escape(regex) + r"\b", text) or regex in text:
                    return intent
        return None

    def extract_target(self, text: str, intent: str) -> str:
        """Extracts the specific app name if mentioned, otherwise returns 'it'."""
        text = text.lower().strip()
        
        # If user says "close chrome", we want "chrome"
        # If user says "close it", we want "it"
        
        # Simple extraction: remove the keyword and return what's left
        keywords = self.patterns.get(intent, [])
        target = text
        for kw in keywords:
            target = target.replace(kw, "")
            
        target = target.replace("this", "").replace("the", "").replace("app", "").strip()
        
        if not target or target in ["it", "eta", "ota"]:
            return "it"
            
        return target

# Global Access
_control_parser = ControlIntentParser()

def parse_control_intent(text: str):
    intent = _control_parser.detect_intent(text)
    if intent:
        target = _control_parser.extract_target(text, intent)
        return {"intent": intent, "target": target}
    return None
