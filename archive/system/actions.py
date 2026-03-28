# =========================
# S1 ASSISTANT ACTIONS
# Phase 4: Dynamic Action Engine
# =========================

import os
import subprocess
import platform
from core.config import APP_MAP

def get_os():
    """Detect operating system. Returns 'win', 'linux', or 'mac'."""
    os_name = platform.system().lower()
    if "windows" in os_name:
        return "win"
    elif "linux" in os_name:
        return "linux"
    elif "darwin" in os_name:
        return "mac"
    return "unknown"

def open_app(app_name: str):
    """
    Opens a supported application using the dynamic APP_MAP.
    """
    os_name = get_os()
    if app_name in APP_MAP and os_name in APP_MAP[app_name]:
        command = APP_MAP[app_name][os_name]
        try:
            # Use shell=True for commands like 'start chrome' or 'taskkill'
            is_shell_needed = "start" in command or "http" in command
            subprocess.Popen(command, shell=is_shell_needed)
            print(f"[ACTION] Executed open command for '{app_name}': {command}")
        except Exception as e:
            print(f"[ACTION ERROR] Could not open '{app_name}'. Command: {command}. Error: {e}")
    else:
        print(f"[ACTION WARN] App '{app_name}' not configured for OS '{os_name}'.")

def close_app(app_name: str):
    """
    Closes a supported application.
    This is OS-specific and can be tricky. We'll use taskkill for Windows.
    """
    os_name = get_os()
    if app_name not in APP_MAP:
        print(f"[ACTION WARN] App '{app_name}' not found in APP_MAP for closing.")
        return

    # Use the executable name from the APP_MAP for closing
    executable = os.path.basename(APP_MAP[app_name].get(os_name, app_name))
    
    try:
        if os_name == "win":
            # taskkill is a reliable way to close apps on Windows
            # /F for force, /IM for image name
            command = f"taskkill /f /im {executable}"
            subprocess.run(command, shell=True, check=True, capture_output=True)
            print(f"[ACTION] Executed close command for '{app_name}': {command}")
        elif os_name in ["linux", "mac"]:
            # pkill is common on Unix-like systems
            command = f"pkill -f {executable}"
            subprocess.run(command, shell=True, check=True, capture_output=True)
            print(f"[ACTION] Executed close command for '{app_name}': {command}")
    except subprocess.CalledProcessError:
        print(f"[ACTION ERROR] Failed to close '{app_name}'. It might not have been running.")
    except Exception as e:
        print(f"[ACTION ERROR] Could not close '{app_name}'. Error: {e}")


def perform_action(action_type: str, entity: str):
    """
    Central action router.
    """
    if action_type == "open":
        open_app(entity)
    elif action_type == "close":
        close_app(entity)
    else:
        print(f"[ACTION] Unknown action type: {action_type}")