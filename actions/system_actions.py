# actions/system_actions.py
import os

# Security Layer: Whitelist of allowed applications
ALLOWED_APPS = ["chrome", "notepad", "calc"]

def open_app(action_data: str):
    """Executes a system-level action (e.g., opening an app)."""
    if action_data not in ALLOWED_APPS:
        return False, f"Access Denied: '{action_data}' is not in the allowed list."
        
    # Execute only if whitelisted
    try:
        os.system(f"start {action_data}")
        return True, f"App {action_data} opened"
    except Exception as e:
        return False, f"Error opening app: {str(e)}"
