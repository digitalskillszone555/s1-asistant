# system/app_state.py
# S1 Assistant - App State Tracker
# Focus: Tracking active and background processes launched by the assistant.

import psutil
import os
import time

class AppStateTracker:
    """
    Monitors process states to determine if an app is still running.
    """
    def __init__(self):
        self.tracked_processes = {} # { "alias": psutil.Process }

    def add_process(self, alias: str, pid: int):
        """Adds a process ID to the tracker."""
        try:
            proc = psutil.Process(pid)
            self.tracked_processes[alias.lower()] = proc
            print(f"[AppState] Now tracking '{alias}' (PID: {pid})")
        except psutil.NoSuchProcess:
            print(f"[AppState WARN] Could not track PID {pid}, process already finished.")

    def is_running(self, alias: str) -> bool:
        """Checks if a specific tracked app is still active."""
        proc = self.tracked_processes.get(alias.lower())
        if not proc:
            return False
        
        try:
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def get_active_apps(self) -> list:
        """Returns a list of all currently running tracked apps."""
        active = []
        for alias in list(self.tracked_processes.keys()):
            if self.is_running(alias):
                active.append(alias)
            else:
                # Clean up finished processes
                del self.tracked_processes[alias]
        return active

# Global Access
_app_state_instance = AppStateTracker()

def get_app_state():
    return _app_state_instance
