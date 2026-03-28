# skills/app_control.py
# Windows-focused application control using the Smart App Resolver.

import subprocess
import time
from skills.base_skill import BaseSkill
from skills.app_resolver import get_app_resolver
# from skills.router import route_skill # To delegate web actions

class AppControlSkill(BaseSkill):
    """
    Skill for controlling applications using the AppResolver to find them.
    Supports opening, closing, restarting, and managing app windows.
    """
    def __init__(self):
        super().__init__(
            name="App Control Skill",
            supported_intents=[
                "open_app", "close_app", "restart_app",
                "minimize_app", "maximize_app", "switch_to_app"
            ]
        )
        self.resolver = get_app_resolver()

    def execute(self, intent: str, entity: str, **kwargs) -> str:
        alias = entity.lower()
        resolved_app = self.resolver.resolve(alias)

        if not resolved_app:
            return f"Sorry, I don't know the application '{alias}'."

        if intent == "open_app":
            return self._open_app(alias, resolved_app)
        elif intent == "close_app":
            return self._close_app(alias, resolved_app)
        elif intent == "restart_app":
            return self._restart_app(alias, resolved_app)
        elif intent in ["minimize_app", "maximize_app", "switch_to_app"]:
            return self._manage_app_window(alias, resolved_app, intent)
        
        return f"Unknown intent '{intent}' for App Control."

    def _open_app(self, alias: str, resolved_app: dict) -> str:
        app_type = resolved_app.get("type")
        if app_type == "app":
            command = resolved_app.get("command")
            try:
                subprocess.Popen(command, shell=True)
                return f"Opening {alias}."
            except Exception as e:
                print(f"[AppControlSkill] Error opening {alias}: {e}")
                return f"Sorry, I couldn't open {alias}."
        elif app_type == "web":
            url = resolved_app.get("url")
            # Delegate to WebControlSkill to open the URL
            return route_skill("open_website", entity=url)
        return f"Don't know how to open '{alias}'."

    def _close_app(self, alias: str, resolved_app: dict) -> str:
        if resolved_app.get("type") != "app":
            return f"'{alias}' is a web page, not a local application I can close."
        
        executable_name = resolved_app.get("executable")
        try:
            # Forcefully terminate the process by its image name
            subprocess.run(f"taskkill /f /im {executable_name}", check=True, shell=True, capture_output=True)
            return f"Closed {alias}."
        except subprocess.CalledProcessError:
            return f"{alias} was not running."
        except Exception as e:
            print(f"[AppControlSkill] Error closing {alias}: {e}")
            return f"Sorry, I couldn't close {alias}."

    def _restart_app(self, alias: str, resolved_app: dict) -> str:
        if resolved_app.get("type") != "app":
            return f"I can't restart a web page like '{alias}'."
        
        self._close_app(alias, resolved_app)
        time.sleep(2) # Wait a moment for the process to terminate
        return self._open_app(alias, resolved_app)

    def _manage_app_window(self, alias: str, resolved_app: dict, action: str) -> str:
        """
        Placeholder for window management.
        For full functionality, this would require a library like 'pygetwindow'.
        """
        if resolved_app.get("type") != "app":
            return f"I can't manage a window for a web page like '{alias}'."

        print(f"[AppControlSkill] Placeholder for action '{action}' on app '{alias}'.")
        return f"Sorry, I can't fully {action.replace('_', ' ')} yet. This feature is under development."

