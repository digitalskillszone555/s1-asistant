# skills/system_control.py
import subprocess
import os
import sys
from skills.base_skill import BaseSkill

class SystemControlSkill(BaseSkill):
    """
    Skill for controlling system-level actions like shutdown, restart, sleep, and locking.
    Initially focused on Windows, but designed for extensibility.
    """
    def __init__(self):
        super().__init__("SystemControl", ["shutdown_system", "restart_system", "sleep_system", "lock_system"])

    def execute(self, intent: str, entity: str, **kwargs) -> str:
        if intent == "shutdown_system":
            return self._shutdown_system()
        elif intent == "restart_system":
            return self._restart_system()
        elif intent == "sleep_system":
            return self._sleep_system()
        elif intent == "lock_system":
            return self._lock_system()
        else:
            return f"System control intent '{intent}' not recognized."

    def _shutdown_system(self) -> str:
        """Shuts down the operating system."""
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/s", "/t", "0"])
            return "Shutting down the system now."
        elif sys.platform == "linux":
            subprocess.run(["sudo", "shutdown", "-h", "now"])
            return "Shutting down the system now."
        elif sys.platform == "darwin":
            subprocess.run(["sudo", "shutdown", "-h", "now"])
            return "Shutting down the system now."
        else:
            return "System shutdown not supported on this OS."

    def _restart_system(self) -> str:
        """Restarts the operating system."""
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/r", "/t", "0"])
            return "Restarting the system now."
        elif sys.platform == "linux":
            subprocess.run(["sudo", "reboot"])
            return "Restarting the system now."
        elif sys.platform == "darwin":
            subprocess.run(["sudo", "reboot"])
            return "Restarting the system now."
        else:
            return "System restart not supported on this OS."

    def _sleep_system(self) -> str:
        """Puts the operating system to sleep."""
        if sys.platform == "win32":
            # Windows command to put system to sleep (requires powercfg utility)
            # This is more complex than a direct 'shutdown' command.
            # Using 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0' or similar
            # For simplicity, will use a placeholder or more reliable method if one exists.
            # A direct command often requires specific privileges or external tools.
            # For this MVP, we'll indicate it's not directly implemented via subprocess.
            # A more robust solution might involve sending WM_SYSCOMMAND message.
            # For now, it's a message.
            return "System sleep is not directly supported via simple command yet. Consider using a dedicated tool or API."
        elif sys.platform == "darwin":
            # For macOS, 'pmset sleepnow'
            subprocess.run(["pmset", "sleepnow"])
            return "Putting the system to sleep."
        else: # Linux
            # Systemd based sleep
            subprocess.run(["sudo", "systemctl", "suspend"])
            return "Putting the system to sleep."


    def _lock_system(self) -> str:
        """Locks the user's session."""
        if sys.platform == "win32":
            # Locks the workstation immediately
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "Locking the workstation."
        elif sys.platform == "linux":
            # Requires a desktop environment lock command (e.g., gnome-screensaver-command -l)
            # This is highly dependent on the user's desktop environment.
            # For simplicity, we'll return a message.
            return "System lock not directly supported via simple command yet. Requires desktop environment specific command."
        elif sys.platform == "darwin":
            # Locks the screen on macOS
            subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "q" using {control down, command down}'])
            return "Locking the screen."
        else:
            return "System lock not supported on this OS."