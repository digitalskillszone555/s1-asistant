# ai/ai_router.py
# S1 Assistant - AI Router (PRODUCTION READY)
# Focus: Intelligent hybrid routing with keyword-based online detection.

import socket
import os
import json
from ai.ai_engine import get_ai_engine
from user.user_manager import get_user_manager
from system.ai_mode_manager import get_ai_mode_manager

def get_user_memory():
    """Loads user memory from file."""
    try:
        if os.path.exists("memory_data/user_memory.json"):
            with open("memory_data/user_memory.json", "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"memory": []}

def save_user_memory_item(key: str, value: str):
    """Saves a single key-value pair to user memory intelligently with validation."""
    try:
        # Validation Layer: Protect memory from poor data
        if not value or not isinstance(value, str):
            return
            
        clean_val = value.strip()
        
        # 1. Name validation (> 2 chars)
        if key == "name" and len(clean_val) <= 2:
            print(f"[Memory Guard] Rejected name '{clean_val}' (too short)")
            return
            
        # 2. Preferences/Habits validation (must be meaningful)
        if key in ["preferences", "habits"] and len(clean_val) < 5:
            print(f"[Memory Guard] Rejected {key} '{clean_val}' (not meaningful)")
            return

        memory_data = {"user_id": "default", "memory": []}
        file_path = "memory_data/user_memory.json"
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                memory_data = json.load(f)
                
        found = False
        for item in memory_data.setdefault("memory", []):
            if item["key"] == key:
                if key in ["preferences", "habits"]:
                    if clean_val.lower() not in item["value"].lower():
                        if item["value"] and item["value"] != "None set":
                            item["value"] = f"{item['value']}, {clean_val}"
                        else:
                            item["value"] = clean_val
                else:
                    item["value"] = clean_val
                found = True
                break
                
        if not found:
            memory_data["memory"].append({"key": key, "value": clean_val})
            
        os.makedirs("memory_data", exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(memory_data, f, indent=2)
    except Exception as e:
        print(f"Memory save error: {e}")

def extract_and_save_memory(prompt: str):
    """Extracts identity, preferences, and habits from prompt."""
    text = prompt.lower().strip()
    
    # 1. Name
    if "my name is " in text:
        parts = text.split("my name is ")
        if len(parts) > 1:
            name = parts[-1].strip(".!?, ").split()[0]
            if name:
                save_user_memory_item("name", name.title())
                
    # 2. Preferences
    if "i like " in text:
        pref = text.split("i like ")[-1].strip(".!?, ")
        if pref:
            save_user_memory_item("preferences", f"likes {pref}")
            
    # 3. Habits
    if "i usually " in text:
        habit = text.split("i usually ")[-1].strip(".!?, ")
        if habit:
            save_user_memory_item("habits", f"usually {habit}")

def detect_emotion(text: str):
    """Detects basic user emotions from text."""
    text_lower = text.lower()
    if any(word in text_lower for word in ["sad", "tired", "alone"]):
        return "low"
    if any(word in text_lower for word in ["angry", "hate", "frustrated"]):
        return "angry"
    if any(word in text_lower for word in ["happy", "great", "awesome"]):
        return "happy"
    return "normal"

# Keywords that trigger online AI (Gemini) over local AI (Ollama)
ONLINE_COMMAND_KEYWORDS = [
    "search for", "search", "google", "find information on",
    "news", "latest headlines", "weather", "forecast",
    "youtube", "play video", "what is", "who is", "when is", 
    "where is", "define", "meaning of"
]

def _is_internet_available():
    """Checks for a live internet connection with a 2s timeout."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def is_online_command(prompt: str) -> bool:
    """Detects if a prompt likely needs real-time online data."""
    command = prompt.lower()
    return any(kw in command for kw in ONLINE_COMMAND_KEYWORDS)

def get_ai_response(prompt: str):
    """
    Unified AI routing logic with rule-based fallback (Temporary AI).
    """
    extract_and_save_memory(prompt)
    
    clean_prompt = prompt.lower().strip()
    
    # --- Temporary AI: Rule-based Replies ---
    if "hello" in clean_prompt or "hi " in clean_prompt or clean_prompt == "hi":
        return "Hello! I am S1, your AI assistant."
    
    if "time" in clean_prompt:
        import datetime
        return f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."
    
    if "date" in clean_prompt:
        import datetime
        return f"Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}."

    # Detect Emotion
    user_emotion = detect_emotion(prompt)

    # Load Memory & Inject into Prompt
    from memory.memory_engine import get_memory_engine
    memory_engine = get_memory_engine()
    memory_summary = memory_engine.get_user_profile_summary()
    
    user_memory = get_user_memory()
    memory_map = {m['key']: m['value'] for m in user_memory.get("memory", [])}
    
    name = memory_map.get("name", "User")
    preferences = memory_map.get("preferences", "None set")
    habits = memory_map.get("habits", "None set")

    system_context = (
        f"You are S1 Assistant. User name: {name}. Preferences: {preferences}. Habits: {habits}. "
        f"User behavior summary: {memory_summary}. "
        f"User emotion: {user_emotion}. Respond naturally and personally. "
        f"If low -> be supportive. If angry -> be calm. If happy -> match energy."
    )
    prompt = f"{system_context}\n\nUser: {prompt}"

    ai_mode_manager = get_ai_mode_manager()
    ai_mode = ai_mode_manager.get_ai_mode()
    ai_engine = get_ai_engine()
    user_manager = get_user_manager()
    user_info = user_manager.get_current_user_info()

    # 1. Forced Online
    if ai_mode == "online":
        return ai_engine.generate_online_response(prompt, user_info)

    # 2. Forced Offline
    elif ai_mode == "offline":
        return ai_engine.generate_offline_response(prompt)

    # 3. Smart Hybrid
    elif ai_mode == "smart":
        has_internet = _is_internet_available()
        
        if has_internet:
            # Route keyword-matched commands directly to online AI
            if is_online_command(prompt):
                res = ai_engine.generate_online_response(prompt, user_info)
                if res: return res
            
            # Try offline first for everything else
            offline_response = ai_engine.generate_offline_response(prompt)
            if offline_response and "unavailable" not in offline_response.lower():
                return offline_response
            
            # Fallback to online if offline fails
            res = ai_engine.generate_online_response(prompt, user_info)
            if res: return res
        
        else:
            # No internet fallback
            return ai_engine.generate_offline_response(prompt)

    # --- Final Rule-Based Fallback (if all AI fails) ---
    return "I'm having trouble connecting to my brain right now, but I'm still here to help with system commands!"
