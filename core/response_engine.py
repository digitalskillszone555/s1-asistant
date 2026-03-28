# core/response_engine.py
# S1 Assistant - Human Response Engine
# Focus: Transforming actions and results into natural language with emotion.

from core.personality import get_personality

class ResponseEngine:
    """
    Translates intents and their execution results into 
    human-style conversational responses with emotional awareness.
    """
    def __init__(self):
        self.personality = get_personality()

    def generate(self, intent_data: dict, success: bool = True, emotion: str = "neutral") -> str:
        """
        Generates a conversational response for the current action.
        """
        intent = intent_data.get("intent", "unknown")
        entity = intent_data.get("entity", "it")
        extra_info = intent_data.get("extra_info", "")

        # Handle specific failure cases with human-like messages
        if not success:
            if "couldn't find" in extra_info.lower() or "not find" in extra_info.lower():
                return self.personality.get_template("app_not_found", emotion="confused", app=entity)
            if "permission" in extra_info.lower() or "denied" in extra_info.lower():
                return self.personality.get_template("permission_denied", emotion="neutral")
            return self.personality.get_template("error", emotion="confused")

        # Map the intent to its personality template
        template_name = intent
        if intent == "open_app": template_name = "open_app"
        elif intent == "close_app": template_name = "close_app"
        elif intent == "search_web": template_name = "search_web"
        elif intent == "search_youtube": template_name = "search_youtube"
        elif intent == "confirm_it": template_name = "confirm_it"
        elif intent == "greeting": template_name = "greeting"

        return self.personality.get_template(template_name, emotion=emotion, app=entity, query=entity)

# Global Access
_response_instance = ResponseEngine()

def get_response_engine():
    return _response_instance
