# core/action_engine.py
# S1 Assistant - Unified Action Engine (PRODUCTION HARDENED)
# Focus: Centralized, safe, and modular skill execution.

import subprocess
import platform
import os
import sys
from skills.web_actions import get_web_actions
from skills.file_actions import get_file_actions
from skills.app_resolver_v3 import get_resolver_v3
from security.action_guard import get_action_guard
from utils.logging_utils import log_event

# --- Legacy Skills Functional Wrappers ---
from skills import time, date, weather, system_info

class ActionEngine:
    """
    The unified executor for all S1 Assistant capabilities.
    Integrates security checks and routes intents to specialized modules.
    """
    def __init__(self):
        self.web = get_web_actions()
        self.file = get_file_actions()
        self.resolver = get_resolver_v3()
        self.guard = get_action_guard()

    def execute(self, intent_data: dict) -> str:
        """
        Main entry point for action execution.
        """
        intent = intent_data.get("intent")
        entity = intent_data.get("entity")
        extra_data = intent_data.get("extra_data")

        log_event("ACTION_ENGINE", f"Executing intent: {intent}", entity=entity)

        # 1. Security Validation
        is_safe, msg = self.guard.is_action_safe(intent, entity, extra_data)
        if not is_safe:
            return msg

        try:
            # 2. Intent Routing
            if intent == "open_app":
                return self._handle_open_app(entity)
            
            elif intent == "close_app":
                return self._handle_close_app(entity)
            
            elif intent == "search_web":
                return self.web.search_google(entity)
            
            elif intent == "search_youtube":
                return self.web.search_youtube(entity)
            
            elif intent == "open_url":
                return self.web.open_url(entity)
            
            elif intent == "create_file":
                return self.file.create_file(entity)
            
            elif intent == "write_file":
                return self.file.write_file(entity, extra_data)
            
            elif intent == "open_file":
                return self.file.open_file(entity)
            
            # --- System Control ---
            elif intent == "shutdown_system":
                return self._shutdown_system()
            
            elif intent == "restart_system":
                return self._restart_system()
            
            elif intent == "lock_system":
                return self._lock_system()
            
            # --- Functional Skills ---
            elif intent == "get_time":
                return time.run()
            
            elif intent == "get_date":
                return date.run()
            
            elif intent == "get_weather":
                return weather.run()
            
            elif intent == "system_info":
                return system_info.run()

            return f"I understand the intent '{intent}', but I haven't been taught how to perform it yet."

        except Exception as e:
            log_event("ACTION_ENGINE", f"Execution error: {e}", level="ERROR")
            return f"Sorry, I encountered an error while performing that action."

    def _handle_open_app(self, entity: str) -> str:
        if not entity: return "What should I open?"
        path = self.resolver.resolve(entity)
        if not path: return f"I couldn't find {entity} on this system."
        
        try:
            subprocess.Popen(path, shell=True)
            return f"Opening {entity}..."
        except Exception as e:
            return f"Failed to launch {entity}: {e}"

    def _handle_close_app(self, entity: str) -> str:
        if not entity: return "What should I close?"
        if platform.system().lower() != "windows":
            return "App closing is currently only supported on Windows."
            
        try:
            target = entity if entity.endswith(".exe") else f"{entity}.exe"
            subprocess.run(f"taskkill /f /im {target}", shell=True, capture_output=True)
            return f"Closed {entity}."
        except Exception as e:
            return f"Could not close {entity}: {e}"

    def _shutdown_system(self) -> str:
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/s", "/t", "60"]) # 60s delay for safety
            return "System will shut down in 60 seconds."
        return "Shutdown only supported on Windows in this version."

    def _restart_system(self) -> str:
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/r", "/t", "60"])
            return "System will restart in 60 seconds."
        return "Restart only supported on Windows."

    def _lock_system(self) -> str:
        if sys.platform == "win32":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "Locking your computer."
        return "Locking only supported on Windows."

# Global Access
_action_engine_instance = None

def get_action_engine():
    global _action_engine_instance
    if _action_engine_instance is None:
        _action_engine_instance = ActionEngine()
    return _action_engine_instance
