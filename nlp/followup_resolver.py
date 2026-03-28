# nlp/followup_resolver.py
# S1 Assistant - Follow-up Context Resolver (Enhanced)
# Focus: Priority-based context resolution with confidence scores.

from memory.conversation_memory import get_conversation_memory

class FollowupResolver:
    """
    Intelligently resolves ambiguous commands based on conversation history.
    Priority: 1. last_app, 2. last_entity, 3. last_intent
    """
    def __init__(self):
        self.memory = get_conversation_memory()
        self.confidence_threshold = 0.7

    def resolve(self, current_intent_data: dict) -> tuple:
        """
        Refines the current intent data using previous context.
        Returns: (resolved_intent_data, confidence)
        """
        intent = current_intent_data.get("intent")
        entity = current_intent_data.get("entity")
        
        last_app = self.memory.get_last_app()
        last_intent = self.memory.get_last_intent()
        last_entity = self.memory.context.get("last_entity")

        resolved_data = current_intent_data.copy()
        confidence = 0.0

        # --- LOGIC 1: APP-SPECIFIC CONTEXT (Priority 1) ---
        if last_app:
            # If last app was youtube, generic search becomes youtube search
            if "youtube" in last_app.lower() and intent == "search_web":
                print(f"[Context] Priority Match: last_app='{last_app}'")
                resolved_data["intent"] = "search_youtube"
                confidence = 0.9
            
            # If last app was a browser, generic URL opening stays in browser
            elif "chrome" in last_app.lower() or "browser" in last_app.lower():
                if intent == "search_web":
                    confidence = 0.8 # Already correct, but strengthens decision

        # --- LOGIC 2: ENTITY-SPECIFIC CONTEXT (Priority 2) ---
        if confidence < self.confidence_threshold and last_entity:
            # If we were just talking about a file, and now user says "write ..."
            if intent == "write_file":
                # If the current entity is NOT a filename, it's likely the text content
                is_filename = entity and "." in entity and entity.split(".")[-1] in ["txt", "md", "py", "json"]
                
                if not is_filename and last_entity.endswith((".txt", ".md", ".py")):
                    print(f"[Context] Priority Match: last_entity='{last_entity}'")
                    resolved_data["entity"] = last_entity
                    resolved_data["extra_data"] = entity # Treat the original entity as text content
                    confidence = 0.85

        # --- LOGIC 3: INTENT-SPECIFIC CONTEXT (Priority 3) ---
        if confidence < self.confidence_threshold and last_intent:
            # If the last thing we did was search, and user provides just a query
            if intent == "unknown" and last_intent in ["search_web", "search_youtube"]:
                # User just said a noun/phrase after a search command
                # (This requires higher level NLP to be sure, but we'll flag it)
                pass 

        # Final Check: If confidence is high, return the resolved data
        if confidence >= self.confidence_threshold:
            print(f"[Decision] Contextual override successful (Score: {confidence})")
            return resolved_data, confidence
        
        return current_intent_data, 0.0

# Global Access
_followup_instance = FollowupResolver()

def get_followup_resolver():
    return _followup_instance
