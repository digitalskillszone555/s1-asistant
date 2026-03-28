# ai/ai_engine.py

import os
import time
import ollama
import google.generativeai as genai
from config.ai_config import OFFLINE_AI_CONFIG, ONLINE_AI_CONFIG

class AIEngine:
    def __init__(self):
        self.online_model_name = ONLINE_AI_CONFIG.get("model")
        self.offline_model_name = OFFLINE_AI_CONFIG.get("model")
        
        # --- Rate Limiting Simulation ---
        self.user_api_calls = {} # { "username": {"date": "YYYY-MM-DD", "count": 0} }
        self.rate_limits = {
            "free": 100, # Max online calls per day for free users
            "pro": 2000  # Max online calls per day for pro users
        }

    def _is_rate_limited(self, user_info):
        """Checks if the user has exceeded their daily online API call limit."""
        username = user_info.get("username", "default")
        user_plan = user_info.get("plan", "free")
        limit = self.rate_limits.get(user_plan, 100)
        
        today = time.strftime("%Y-%m-%d")
        
        if username not in self.user_api_calls:
            self.user_api_calls[username] = {"date": today, "count": 0}

        # Reset count if it's a new day
        if self.user_api_calls[username]["date"] != today:
            self.user_api_calls[username] = {"date": today, "count": 0}

        if self.user_api_calls[username]["count"] >= limit:
            print(f"[AI Engine] User '{username}' has reached their daily limit of {limit} online API calls.")
            return True
        
        return False

    def _increment_rate_limit_count(self, username: str):
        """Increments the API call count for a user."""
        if username in self.user_api_calls:
            self.user_api_calls[username]["count"] += 1

    def generate_online_response(self, prompt: str, user_info: dict):
        """Generates a response from Gemini, checking rate limits."""
        api_key = ONLINE_AI_CONFIG.get("api_key")
        username = user_info.get("username", "default")

        if not api_key:
            return None # Not configured
        
        if self._is_rate_limited(user_info):
            return None # User has hit their limit

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(self.online_model_name)
            # Add 10s timeout
            response = model.generate_content(prompt, request_options={"timeout": 10})
            
            self._increment_rate_limit_count(username)
            print(f"[AI Engine] Online response generated for '{username}'. Daily count: {self.user_api_calls[username]['count']}")
            return response.text
        except Exception as e:
            print(f"[AI Engine ERROR] Online generation failed: {e}")
            return None

    def generate_offline_response(self, prompt: str):
        """Generates a response from the local Ollama model with basic safety."""
        try:
            # We assume Ollama is running and responsive. 
            # Real timeouts would require a wrapper thread.
            response = ollama.chat(
                model=self.offline_model_name,
                messages=[{'role': 'user', 'content': prompt}],
                stream=False
            )
            return response['message']['content']
        except Exception as e:
            print(f"[AI Engine ERROR] Offline generation failed: {e}")
            return "I'm sorry, my local AI service is currently unavailable."

# Global instance
S1_AI_ENGINE = AIEngine()

def get_ai_engine():
    return S1_AI_ENGINE
