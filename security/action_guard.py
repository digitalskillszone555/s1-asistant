# security/action_guard.py
# S1 Assistant - Action Guard (PRODUCTION HARDENED)
# Focus: Comprehensive security layer to block dangerous system/file commands.

import os
from datetime import datetime
from utils.logging_utils import log_event

class ActionGuard:
    """
    Hardened security filter that validates actions before execution.
    Combines keyword blocking, character filtering, and path validation.
    """
    def __init__(self):
        # Layer 1: Dangerous Keywords
        self.banned_keywords = {
            "rm -rf", "format", "del /s", "drop table", 
            "shutdown -s", "poweroff", "reboot", "erase",
            "system32", "/etc/shadow", "/etc/passwd",
            "mkfs", "dd", "powershell", "regedit",
            "set-mppreference", "disablerealtimemonitoring"
        }
        
        # Layer 2: Forbidden characters for command injection
        self.forbidden_chars = {'&', '|', ';', '>', '<', '`', '$', '(', ')', '!'}

        # Layer 3: Allowed file extensions
        self.allowed_extensions = {".txt", ".md", ".json", ".log", ".py"}
        
        # Layer 4: Protected System Paths
        self.protected_paths = self._get_protected_paths()
        
        # Layer 5: Allowed Base Directories
        home = os.path.expanduser("~")
        self.safe_dirs = {
            home,
            os.path.join(home, "Downloads"),
            os.path.join(home, "Documents"),
            os.path.join(home, "Desktop"),
        }

    def _get_protected_paths(self) -> set:
        paths = set()
        if os.name == 'nt':
            paths.add(os.environ.get('WinDir', 'C:\\Windows').lower())
            paths.add(os.environ.get('ProgramFiles', 'C:\\Program Files').lower())
        else:
            paths.update(['/etc', '/bin', '/sbin', '/usr/bin', '/var'])
        return paths

    def is_action_safe(self, intent: str, entity: str, extra_data: str = None) -> (bool, str):
        """
        Comprehensive security check.
        Returns: (is_safe: bool, message: str)
        """
        if not entity and not extra_data:
            return True, "Safe"

        check_text = f"{entity or ''} {extra_data or ''}".lower()

        # 1. Keyword Check
        if any(kw in check_text for kw in self.banned_keywords):
            log_event("SECURITY", f"BLOCKED: Dangerous keyword in '{intent}'", level="ERROR", entity=entity)
            return False, "Action blocked: Security risk detected."

        # 2. Injection Character Check
        if any(char in check_text for char in self.forbidden_chars):
            log_event("SECURITY", f"BLOCKED: Forbidden chars in '{intent}'", level="ERROR", entity=entity)
            return False, "Action blocked: Forbidden characters detected."

        # 3. Path & Extension Validation
        if intent in ["create_file", "write_file", "open_file", "delete_file"]:
            return self._validate_path(intent, entity)

        return True, "Safe"

    def _validate_path(self, intent: str, path: str) -> (bool, str):
        if not path:
            return False, "No file path provided."
            
        try:
            # Check Extension
            if "." in path:
                ext = "." + path.rsplit(".", 1)[-1].lower()
                if ext not in self.allowed_extensions:
                    return False, f"Action blocked: Unsafe file extension '{ext}'."

            # Canonicalize Path
            abs_path = os.path.abspath(path).lower()

            # Check for system paths
            for prot in self.protected_paths:
                if abs_path.startswith(prot):
                    log_event("SECURITY", f"BLOCKED: System path access '{abs_path}'", level="ERROR")
                    return False, "Action blocked: System directory access is forbidden."

            # Check if in safe directory (strict for write/delete)
            if intent in ["write_file", "delete_file", "create_file"]:
                is_safe = any(abs_path.startswith(os.path.abspath(sd).lower()) for sd in self.safe_dirs)
                if not is_safe:
                    return False, "Action blocked: File operations must be in user directories (Documents, Desktop, etc.)."

        except Exception as e:
            return False, f"Invalid path resolution: {e}"

        return True, "Safe"

# Global Access
_guard_instance = ActionGuard()

def get_action_guard():
    return _guard_instance
