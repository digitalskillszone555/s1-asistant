# security/permission_manager.py
# S1 Assistant - Permission Manager
# Focus: Classify actions by risk level and enforce permission checks.

class PermissionManager:
    """
    Classifies actions and determines if explicit user permission is required.
    """
    def __init__(self):
        self.risk_levels = {
            "open_app": "SAFE",
            "search_web": "SAFE",
            "search_youtube": "SAFE",
            "open_url": "SAFE",
            
            "create_file": "MEDIUM",
            "write_file": "MEDIUM",
            "open_file": "MEDIUM",
            
            "delete_file": "DANGEROUS",
            "close_app": "DANGEROUS",
            "kill_process": "DANGEROUS"
        }

    def get_risk_level(self, intent: str) -> str:
        """Returns the risk level of a given intent."""
        return self.risk_levels.get(intent, "MEDIUM") # Default to MEDIUM if unknown

    def needs_permission(self, intent: str, user_trusted: bool = False) -> bool:
        """
        Determines if an action requires explicit permission.
        SAFE: Never ask.
        MEDIUM: Ask unless user is highly trusted (habit).
        DANGEROUS: Always ask.
        """
        risk = self.get_risk_level(intent)
        
        if risk == "SAFE":
            return False
        elif risk == "MEDIUM":
            return not user_trusted
        elif risk == "DANGEROUS":
            return True
        return True

# Global Access
_permission_instance = PermissionManager()

def get_permission_manager():
    return _permission_instance
