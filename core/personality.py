# core/personality.py
# S1 Assistant - Personality Layer (EMOTIONALLY INTELLIGENT)
# Focus: Defining assistant tone, styles, and adaptive emotions.

import random

class Personality:
    """
    Defines distinct personality styles and adaptive emotional tones.
    Angry User -> Calm Tone
    Sad User -> Supportive Tone
    Happy User -> Energetic Tone
    Confused User -> Simple Explanation
    """
    def __init__(self, mode="friendly"):
        self.mode = mode
        
        self.templates = {
            "friendly": {
                "open_app": ["Alright, opening {app} for you.", "Got it, launching {app} right now.", "Sure thing, opening {app}."],
                "close_app": ["Done! I've closed {app}.", "Alright, {app} is now closed.", "Successfully closed {app}."],
                "search_web": ["Searching Google for '{query}'...", "Looking that up on Google for you.", "Searching for '{query}' now."],
                "search_youtube": ["Finding '{query}' on YouTube...", "Searching YouTube for you.", "Looking for '{query}' videos."],
                "confirm_it": ["Okay, I'll keep that in mind.", "Got it, I'll remember that.", "Noted!"],
                "error": ["Oops, something went wrong there.", "I'm sorry, I couldn't do that.", "Sorry, I ran into an error."],
                "greeting": ["Hey! How can I help you today?", "Hello! What can I do for you?", "Hi there! Ready to help."],
                
                # --- Adaptive Emotional Overlays ---
                "happy": ["I'm happy to help! {base}", "Great! {base}", "Awesome, {base}"],
                "neutral": ["{base}"],
                "confused": ["I'm not exactly sure, but {base}", "Let me explain simply: {base}", "Hmm, {base}"],
                "angry": ["I understand. {base}", "Let's take it one step at a time. {base}", "Calmly, {base}"],
                "sad": ["I'm here for you. {base}", "I'm sorry you feel that way. {base}", "Hope this helps: {base}"],
                
                # Human-like Error handling
                "app_not_found": ["I searched everywhere, but I couldn't find {app} on your system.", "It looks like {app} isn't installed. Should I search for it online?"],
                "permission_denied": ["I'd love to help, but I don't have permission to do that.", "For security reasons, I'm not allowed to perform that action."],
            },
            "fast": {
                "open_app": ["Opening {app}.", "Launching {app}.", "{app} open."],
                "close_app": ["Closed {app}.", "Closing {app}.", "Terminated {app}."],
                "search_web": ["Searching Google.", "Searching...", "Querying Google."],
                "search_youtube": ["Searching YouTube.", "Querying YouTube.", "Finding videos."],
                "confirm_it": ["Noted.", "Okay.", "Done."],
                "error": ["Failed.", "Error.", "Couldn't do that."]
            }
        }

    def get_template(self, intent, emotion="neutral", **kwargs):
        """Returns a random variation for the given intent, style, and emotion."""
        style_templates = self.templates.get(self.mode, self.templates["friendly"])
        
        # 1. Get base intent template
        intent_templates = style_templates.get(intent, style_templates.get("confirm_it", ["Okay."]))
        base_template = random.choice(intent_templates)
        
        # 2. Apply formatting to base
        try:
            formatted_base = base_template.format(**kwargs)
        except (KeyError, IndexError):
            formatted_base = base_template

        # 3. Apply adaptive emotional overlay
        if self.mode == "friendly" and emotion in style_templates:
            emotion_template = random.choice(style_templates[emotion])
            return emotion_template.format(base=formatted_base)
            
        return formatted_base

# Global Access
_personality_instance = Personality(mode="friendly")

def get_personality():
    return _personality_instance
