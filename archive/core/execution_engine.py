# core/execution_engine.py
# S1 Assistant - Execution Engine V2
# Focus: Reliable application launching using resolved paths.

import subprocess
import os
import platform
from skills.app_resolver_v2 import get_resolver_v2

class ExecutionEngineV2:
    """
    Handles the actual execution of intents by coordinating with resolvers and OS.
    """
    def __init__(self):
        self.resolver = get_resolver_v2()

    def execute_intent(self, intent_data: dict) -> str:
        """
        Receives {intent, entity} and performs the action.
        """
        intent = intent_data.get("intent")
        entity = intent_data.get("entity")

        if not intent or intent == "unknown":
            return "I'm sorry, I don't understand that command."

        if intent == "open_app":
            return self._open_app(entity)
        elif intent == "close_app":
            return self._close_app(entity)
        
        return f"The action '{intent}' is not yet supported in the V2 engine."

    def _open_app(self, entity: str) -> str:
        """Locates and opens the requested application."""
        if not entity:
            return "What application would you like me to open?"

        app_path = self.resolver.resolve(entity)
        
        if not app_path:
            return f"I couldn't find '{entity}' on your computer."

        try:
            # shell=True is needed for some Windows system shortcuts/commands
            # No wait: we want to launch and return control immediately
            subprocess.Popen(app_path, shell=True)
            return f"Opening {entity}..."
        except Exception as e:
            print(f"[ExecV2 ERROR] Failed to launch {entity} at {app_path}: {e}")
            return f"An error occurred while trying to open {entity}."

    def _close_app(self, entity: str) -> str:
        """Closes the requested application by task killing its process."""
        if not entity:
            return "What application would you like me to close?"

        # Try taskkill for Windows
        if platform.system().lower() == "windows":
            try:
                # Resolve it first to get the correct executable name (e.g., 'chrome' -> 'chrome.exe')
                # But taskkill works better with just the image name.
                # We'll try the entity name directly + .exe if needed.
                img_name = f"{entity}.exe" if not entity.endswith(".exe") else entity
                
                # Check resolver to see if we have a mapped executable name
                # (Simple check: reuse app_map logic internally if needed)
                # For now, use the image name directly for taskkill.
                
                cmd = f"taskkill /f /im {img_name}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return f"Successfully closed {entity}."
                else:
                    return f"It doesn't look like {entity} is currently running."
            except Exception as e:
                print(f"[ExecV2 ERROR] Close failed: {e}")
                return f"Sorry, I couldn't close {entity}."
        
        return f"Closing applications is currently only supported on Windows."

# Singleton instance
_engine_instance = None

def get_execution_engine_v2():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ExecutionEngineV2()
    return _engine_instance

# Wrapper for easy access
def run_command_v2(intent_data: dict) -> str:
    return get_execution_engine_v2().execute_intent(intent_data)
