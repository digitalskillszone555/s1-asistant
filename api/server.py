# api/server.py

import uvicorn
import threading
import asyncio # New import for managing server loop
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.master_brain_v7 import process_command_master_v7
from utils.state import get_state_manager, AssistantState
from system.mode_manager import get_mode_manager
from user.user_manager import get_user_manager
from language.language_manager import get_language_manager
from memory.memory_engine import get_memory_engine
from memory.conversation_memory import get_conversation_memory
from utils.logging_utils import log_event # Centralized logging
from system.auto_mode import get_auto_mode_manager
from system.config import DEBUG_MODE
from actions.system_actions import open_app
import json
import hashlib
import secrets
import os
from datetime import datetime

# In-memory storage for users (temporary, no database yet)
IN_MEMORY_USERS = {}

# --- Pydantic Models for Request Bodies ---
class AutoModeRequest(BaseModel):
    enabled: bool

class LogActionRequest(BaseModel):
    action: str
    result: str

class LogErrorRequest(BaseModel):
    action: str
    error: str
    retry_result: str

class CommandRequest(BaseModel):
    text: str

class ModeRequest(BaseModel):
    mode: str

class UserRequest(BaseModel):
    username: str

class LanguageRequest(BaseModel):
    language: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class ResetRequest(BaseModel):
    email: str

# --- FastAPI Application ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/login")
async def api_login(request: LoginRequest):
    user = IN_MEMORY_USERS.get(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    password_hash = hashlib.sha256(request.password.encode()).hexdigest()
    if user["password_hash"] != password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    token = secrets.token_hex(16)
    
    return {
        "token": token,
        "user": {
            "email": user["email"],
            "name": user["name"]
        }
    }

@app.post("/api/register")
async def api_register(request: RegisterRequest):
    if request.email in IN_MEMORY_USERS:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = hashlib.sha256(request.password.encode()).hexdigest()
    
    IN_MEMORY_USERS[request.email] = {
        "name": request.name,
        "email": request.email,
        "password_hash": password_hash
    }
    return {"status": "ok", "message": "Registered successfully"}

@app.post("/api/reset")
async def api_reset(request: ResetRequest):
    return {"status": "ok", "message": "Reset email sent"}

@app.get("/api/auto_mode/suggestion")
async def get_auto_suggestion():
    auto_manager = get_auto_mode_manager()
    suggestion = auto_manager.get_latest_suggestion()
    return {"suggestion": suggestion}

@app.post("/api/auto_mode/toggle")
async def toggle_auto_mode(request: AutoModeRequest):
    auto_manager = get_auto_mode_manager()
    auto_manager.set_enabled(request.enabled)
    return {"status": "ok", "enabled": request.enabled}

@app.post("/api/auto_mode/toggle_auto_exec")
async def toggle_auto_exec(request: AutoModeRequest):
    auto_manager = get_auto_mode_manager()
    auto_manager.set_auto_execution(request.enabled)
    return {"status": "ok", "auto_execution": request.enabled}

@app.post("/api/log_action")
async def api_log_action(request: LogActionRequest):
    os.makedirs("logs", exist_ok=True)
    with open("logs/actions.log", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] ACTION: {request.action} | RESULT: {request.result}\n")
    return {"status": "ok"}

@app.post("/api/log_error")
async def api_log_error(request: LogErrorRequest):
    os.makedirs("logs", exist_ok=True)
    with open("logs/errors.log", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] ACTION: {request.action} | ERROR: {request.error} | RETRY RESULT: {request.retry_result}\n")
    return {"status": "ok"}

@app.get("/api/suggestions")
async def api_suggestions():
    return {"suggestions": [
        "What time is it?",
        "What is the weather like?",
        "Tell me a joke",
        "System info"
    ]}

@app.get("/api/self-test")
async def api_self_test():
    from system.self_test import run_self_test
    return run_self_test()

@app.get("/api/full-test")
async def api_full_test():
    from system.integration_test import run_full_system_test
    return run_full_system_test()

@app.get("/api/memory")
async def api_get_memory():
    try:
        if os.path.exists("memory_data/user_memory.json"):
            with open("memory_data/user_memory.json", "r") as f:
                return json.load(f)
        return {"user_id": "default", "memory": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/memory")
async def api_save_memory(request: dict):
    try:
        os.makedirs("memory_data", exist_ok=True)
        with open("memory_data/user_memory.json", "w") as f:
            json.dump(request, f, indent=2)
        return {"status": "ok", "message": "Memory saved"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def generate_proactive_suggestion(actions: list):
    """Predicts and generates a logical next-task suggestion based on current actions and memory."""
    try:
        memory_file = "memory_data/user_memory.json"
        memory = {}
        if os.path.exists(memory_file):
            with open(memory_file, "r") as f:
                mem_data = json.load(f)
                memory = {m['key']: m['value'] for m in mem_data.get("memory", [])}
        
        habits = memory.get("habits", "").lower()
        
        # Action-based logic
        action_data_list = [str(a.get("data", "")).lower() for a in actions]
        
        if "chrome" in action_data_list:
            if "gmail" in habits:
                return "Shall I open your Gmail as well?"
            if "notion" in habits:
                return "Do you want to check your tasks in Notion?"
        
        if "notepad" in action_data_list:
            return "Should I set a reminder for your notes?"

        if any(url in str(action_data_list) for url in ["github", "stackoverflow"]):
            return "Need me to open Slack for team communication?"

    except Exception as e:
        print(f"Suggestion error: {e}")
    
    return "What's next on your list?"

@app.post("/api/command")
async def send_command(request: CommandRequest):
    """Receives a text command and sends it to the S1 core."""
    raw_text = request.text.lower().strip()
    
    # 1. Continuous Task Flow Detection (Multi-task splitting)
    # Detect "and then", "then", "next"
    delimiters = ["and then", "then", "next"]
    tasks = [raw_text]
    for delimiter in delimiters:
        new_tasks = []
        for task in tasks:
            if delimiter in task:
                new_tasks.extend([t.strip() for t in task.split(delimiter) if t.strip()])
            else:
                new_tasks.append(task)
        tasks = new_tasks

    if len(tasks) > 1:
        all_actions = []
        replies = []
        for t in tasks:
            res = await process_single_command(t)
            if "actions" in res:
                all_actions.extend(res["actions"])
            replies.append(res["reply"])
        
        suggestion = await generate_proactive_suggestion(all_actions)
        return {
            "reply": f"{replies[0]} (Starting sequence...)",
            "actions": all_actions,
            "followup": suggestion
        }

    res = await process_single_command(raw_text)
    if res.get("actions"):
        res["followup"] = await generate_proactive_suggestion(res["actions"])
    return res

async def process_single_command(text: str):
    """Helper to process a individual command logic."""
    # 1. Detect built-in commands
    if "open youtube" in text:
        return {
            "reply": "Opening YouTube...",
            "actions": [{"type": "open_url", "data": "https://youtube.com"}]
        }
    elif "open google" in text:
        return {
            "reply": "Opening Google...",
            "actions": [{"type": "open_url", "data": "https://google.com"}]
        }
    elif text == "time" or "what time" in text:
        now = datetime.now().strftime("%H:%M")
        return {
            "reply": f"The current time is {now}",
            "actions": []
        }
    elif "date" in text or "what date" in text:
        today = datetime.now().strftime("%A, %B %d, %Y")
        return {
            "reply": f"Today is {today}",
            "actions": []
        }
    
    # New: App Opening Commands
    elif "open notepad" in text:
        return {
            "reply": "Opening Notepad...",
            "actions": [{"type": "open_app", "data": "notepad"}]
        }
    elif "open calculator" in text:
        return {
            "reply": "Opening Calculator...",
            "actions": [{"type": "open_app", "data": "calc"}]
        }
    elif "open chrome" in text:
        return {
            "reply": "Opening Chrome...",
            "actions": [{"type": "open_app", "data": "chrome"}]
        }
    
    # 2. Automation Chains (Smart & Static)
    elif any(cmd in text for cmd in ["start my work", "open my workspace", "start my day"]):
        # Load Memory for Dynamic Actions
        actions = []
        reply = "Starting your day! Opening your workspace..."
        
        try:
            memory_file = "memory_data/user_memory.json"
            if os.path.exists(memory_file):
                with open(memory_file, "r") as f:
                    mem_data = json.load(f)
                    memory = {m['key']: m['value'] for m in mem_data.get("memory", [])}
                    habits = memory.get("habits", "").lower()
                    prefs = memory.get("preferences", "").lower()
                    
                    # Smart detection from habits/preferences
                    if "chrome" in habits or "chrome" in prefs:
                        actions.append({ "type": "open_app", "data": "chrome" })
                    if "gmail" in habits or "gmail" in prefs:
                        actions.append({ "type": "open_url", "data": "https://mail.google.com" })
                    if "notion" in habits or "notion" in prefs:
                        actions.append({ "type": "open_url", "data": "https://notion.so" })
                    if "github" in habits or "github" in prefs:
                        actions.append({ "type": "open_url", "data": "https://github.com" })
        except Exception as e:
            if DEBUG_MODE:
                print(f"Smart habit error: {e}")

        # Fallback to defaults if no smart actions found
        if not actions:
            actions = [
                { "type": "open_url", "data": "https://calendar.google.com" },
                { "type": "open_url", "data": "https://gmail.com" },
                { "type": "open_url", "data": "https://notion.so" }
            ]
        else:
            reply = "Setting up your personalized workspace... 🚀"

        return {
            "reply": reply,
            "actions": actions
        }

    elif "work mode" in text:
        return {
            "reply": "Switching to work mode. Good luck!",
            "actions": [
                { "type": "open_url", "data": "https://github.com" },
                { "type": "open_url", "data": "https://stackoverflow.com" },
                { "type": "open_url", "data": "https://slack.com" }
            ]
        }

    # 3. Fallback to Gemini
    reply = process_command_master_v7(text)
    return {"reply": reply, "actions": []}


@app.post("/api/execute_action")
async def execute_action(request: dict):
    """Executes a system-level action (e.g., opening an app)."""
    action_type = request.get("type")
    action_data = request.get("data")

    if action_type == "open_app":
        success, message = open_app(action_data)
        if success:
            return {"status": "success", "action": f"open_app:{action_data}", "message": message}
        else:
            return {"status": "failed", "action": f"open_app:{action_data}", "message": message}

    return {"status": "failed", "action": action_type, "message": "Unknown action type"}
@app.get("/reply")
async def get_last_reply():
    """Gets the last spoken reply from the S1 core."""
    memory = get_conversation_memory()
    last_turn = memory.get_last_turn()
    reply = last_turn["assistant"] if last_turn else ""
    return {"reply": reply}

@app.post("/listen")
async def start_listening():
    """Triggers the S1 core to start listening for a voice command."""
    state_manager = get_state_manager()
    state_manager.set_state(AssistantState.WAITING)
    return {"status": "listening"}

@app.post("/stop")
async def stop_listening():
    """Tells the S1 core to stop the current session and go idle."""
    state_manager = get_state_manager()
    state_manager.set_state(AssistantState.IDLE)
    return {"status": "stopped"}

@app.post("/mode")
async def change_mode(request: ModeRequest):
    """Changes the assistant's behavior mode."""
    mode_manager = get_mode_manager()
    success, message = mode_manager.set_mode(request.mode)
    return {"status": "ok", "message": message}

@app.post("/user")
async def switch_user(request: UserRequest):
    """Switches the active user profile."""
    user_manager = get_user_manager()
    lang_manager = get_language_manager()
    success, message = user_manager.switch_user(request.username)
    if success:
        lang_manager.load_user_language()
    return {"status": "ok", "message": message}

@app.post("/language")
async def set_language(request: LanguageRequest):
    """Sets the user's preferred language."""
    lang_manager = get_language_manager()
    memory_engine = get_memory_engine()
    
    lang_code_map = {"english": "en", "bengali": "bn", "hindi": "hi"}
    lang_code = lang_code_map.get(request.language.lower())
    
    if lang_code:
        memory_engine.save_identity("language", lang_code)
        lang_manager.load_language(lang_code)
        reply = lang_manager.get_reply("language_switched", language=request.language)
        return {"status": "ok", "message": reply}
    return {"status": "error", "message": "Unknown language."}

# --- Server Runner ---
def start_api():
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)

y("language_switched", language=request.language)
        return {"status": "ok", "message": reply}
    return {"status": "error", "message": "Unknown language."}

# --- Server Runner ---
def start_api():
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)

