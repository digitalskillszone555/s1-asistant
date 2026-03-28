# nlp/emotion_detector.py
# S1 Assistant - Emotion Detection Module
# Focus: Identifying user emotional tone from text.

class EmotionDetector:
    """
    Analyzes text to detect simple emotional tones:
    happy, angry, confused, sad, neutral.
    """
    def __init__(self):
        self.keywords = {
            "happy": ["great", "awesome", "good", "happy", "thanks", "thank you", "love", "perfect", "excited"],
            "angry": ["bad", "hate", "stupid", "worst", "annoying", "stop", "angry", "kill", "dumb", "useless"],
            "confused": ["what", "how", "why", "who", "where", "confused", "don't know", "unsure", "help", "?"],
            "sad": ["sad", "bad", "unhappy", "sorry", "lonely", "help", "cry", "worst", "depressed"]
        }

    def detect(self, text: str) -> str:
        """Detects the dominant emotion based on keywords."""
        if not text:
            return "neutral"
            
        text_lower = text.lower()
        
        # Simple frequency-based detection
        scores = {"happy": 0, "angry": 0, "confused": 0, "sad": 0}
        
        for emotion, words in self.keywords.items():
            for word in words:
                if word in text_lower:
                    scores[emotion] += 1
                    
        # Get the emotion with the highest score
        max_emotion = max(scores, key=scores.get)
        
        if scores[max_emotion] > 0:
            return max_emotion
            
        return "neutral"

# Global Instance
_detector = EmotionDetector()

def detect_emotion(text: str) -> str:
    return _detector.detect(text)
