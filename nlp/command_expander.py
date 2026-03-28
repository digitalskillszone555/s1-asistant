# nlp/command_expander.py
# S1 Assistant - Command Expansion Module
# Focus: Parsing complex/multi-task commands from raw text.

from nlp.intent_engine_v2 import get_intent_v2

class CommandExpander:
    """
    Analyzes raw text to detect complex patterns and extract extra parameters 
    (like search queries or file content).
    """
    def expand(self, raw_text: str) -> dict:
        """
        Takes raw text and returns a rich intent object.
        Example: "search cats on youtube" -> {intent: search_youtube, entity: cats}
        """
        text = raw_text.lower().strip()
        
        # 1. Start with the standard V2 NLP
        intent_data = get_intent_v2(text)
        
        # 2. Add custom logic for expanded actions
        
        # --- WEB SEARCH PATTERNS ---
        # Special check: If it's an 'open' command, don't force it to search
        if intent_data["intent"] == "open_app" and "youtube" in text:
            return intent_data

        if "youtube" in text:
            # "search [X] on youtube" or "youtube [X]"
            if "search" in text:
                entity = text.replace("search", "").replace("on youtube", "").strip()
            else:
                entity = text.replace("youtube", "").strip()
            
            return {"intent": "search_youtube", "entity": entity}
            
        elif "search" in text:
            # "search [X]" or "google [X]"
            entity = text.replace("search", "").replace("google", "").strip()
            return {"intent": "search_web", "entity": entity}

        # --- FILE PATTERNS ---
        elif "create file" in text:
            # "create file [X].txt"
            entity = text.replace("create file", "").strip()
            return {"intent": "create_file", "entity": entity}

        elif "write" in text and "in" in text:
            # "write [CONTENT] in [FILENAME].txt"
            try:
                content_part = text.split("write", 1)[1].split("in", 1)[0].strip()
                filename_part = text.split("in", 1)[1].strip()
                return {
                    "intent": "write_file", 
                    "entity": filename_part, 
                    "extra_data": content_part
                }
            except IndexError:
                pass

        elif "open file" in text:
            # "open file [X].txt"
            entity = text.replace("open file", "").strip()
            return {"intent": "open_file", "entity": entity}

        # --- FALLBACK ---
        return intent_data

# Global Access
_expander_instance = CommandExpander()

def expand_command(text: str):
    return _expander_instance.expand(text)
