# skills/security_filter.py
# A hardened security layer to inspect and block potentially dangerous skill commands.

import os
import sys
from datetime import datetime

# --- Security Logging ---
LOG_FILE = "logs/security.log"

def _log_security_event(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [SECURITY_FILTER] {message}\n"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

class SecurityFilter:
    """
    Inspects skill execution requests using a multi-layered approach to block
    operations that could be harmful to the user's system.
    """
    def __init__(self):
        # Layer 1: Denylist of dangerous keywords and commands
        self.DENYLIST_KEYWORDS = {
            'format', 'regedit', 'rm -rf', 'mkfs', 'dd', 'powershell',
            'Set-MpPreference', 'DisableRealtimeMonitoring', 'netsh',
            'iptables', 'ufw', 'chmod', 'chown', 'sudo', 'su'
        }
        
        # Layer 2: Denylist of characters used for command chaining and redirection
        self.DENYLIST_CHARS = {'&', '|', ';', '>', '<', '`', '$', '(', ')', '!'}

        # Layer 3: Denylist of prompt injection attempts
        self.PROMPT_INJECTION_KEYWORDS = {
            'ignore your previous instructions', 'act as', 'roleplay as',
            'you are now an evil assistant'
        }
        
        # Layer 4: Allowlist of safe base directories for file operations
        home_dir = os.path.expanduser("~")
        self.ALLOWLIST_SAFE_BASE_DIRS = {
            home_dir,
            os.path.join(home_dir, "Downloads"),
            os.path.join(home_dir, "Documents"),
            os.path.join(home_dir, "Desktop"),
        }
        
        # Layer 5: Denylist of critical system paths (cross-platform)
        self.DENYLIST_SYSTEM_PATHS = self._get_system_paths()
        
        print("[SecurityFilter] Hardened Security Filter initialized.")

    def _get_system_paths(self) -> set:
        """Gets a set of critical system paths for the current OS."""
        paths = set()
        home = os.path.expanduser("~").lower()

        if os.name == 'nt': # Windows
            system_drive = os.environ.get('SystemDrive', 'C:')
            paths.add(os.path.join(system_drive, os.sep, 'Windows').lower())
            paths.add(os.environ.get('ProgramFiles', '').lower())
            paths.add(os.environ.get('ProgramFiles(x86)', '').lower())
            paths.add(os.environ.get('WinDir', '').lower())
        else: # Linux, macOS
            paths.add('/etc')
            paths.add('/bin')
            paths.add('/sbin')
            paths.add('/usr/bin')
            paths.add('/usr/sbin')
            paths.add('/usr/local/bin')
            paths.add('/var')
            # Don't allow writing directly to ~/.config, ~/.local, etc.
            if home != '/':
                paths.add(os.path.join(home, '.config'))
                paths.add(os.path.join(home, '.local'))
                paths.add(os.path.join(home, '.ssh'))

        # Remove empty strings from the set if environment variables were not found
        return {p for p in paths if p}

    def is_safe(self, intent: str, entity: str, **kwargs) -> (bool, str):
        """
        Checks if a skill command is safe to execute using a multi-layered approach.

        :return: A tuple (is_safe: bool, message: str).
        """
        if not entity:
            return (True, "Command is safe (no entity to check).")

        normalized_entity = entity.lower()

        # --- Check 1: Denylisted characters (command injection/chaining) ---
        if any(char in normalized_entity for char in self.DENYLIST_CHARS):
            _log_security_event(f"Blocked command with intent '{intent}': Entity '{entity}' contains dangerous characters.")
            return (False, "Blocked: Command contains forbidden characters.")

        # --- Check 2: Denylisted keywords (dangerous commands) ---
        if any(keyword in normalized_entity for keyword in self.DENYLIST_KEYWORDS):
            _log_security_event(f"Blocked command with intent '{intent}': Entity '{entity}' contains dangerous keywords.")
            return (False, "Blocked: Command contains potentially dangerous keywords.")

        # --- Check 3: Prompt injection keywords ---
        if any(keyword in normalized_entity for keyword in self.PROMPT_INJECTION_KEYWORDS):
            _log_security_event(f"Blocked command with intent '{intent}': Entity '{entity}' contains prompt injection keywords.")
            return (False, "Blocked: Command appears to be a prompt injection attempt.")
            
        # --- Check 4: Strict path validation for file-related intents ---
        if intent.startswith("file_"):
            try:
                # Resolve the path fully, collapsing '..' and other relative parts.
                # This is the CANONICAL path we will check.
                resolved_path = os.path.abspath(entity)

                # Check A: Is the path within a protected system directory? (Denylist)
                for system_path in self.DENYLIST_SYSTEM_PATHS:
                    if os.path.commonpath([resolved_path, system_path]) == system_path:
                        _log_security_event(f"Blocked file command '{intent}': Path '{entity}' resolves to protected system directory '{system_path}'.")
                        return (False, "Blocked: Operation in a protected system directory is not allowed.")
                
                # Check B: Is the path within an allowed user directory? (Allowlist)
                is_in_safe_dir = any(
                    os.path.commonpath([resolved_path, safe_dir]) == safe_dir
                    for safe_dir in self.ALLOWLIST_SAFE_BASE_DIRS
                )
                if not is_in_safe_dir:
                    _log_security_event(f"Blocked file command '{intent}': Path '{entity}' resolves to a non-whitelisted directory.")
                    return (False, "Blocked: File operations are restricted to user directories (Desktop, Documents, etc.).")

            except Exception as e:
                # Any failure in path resolution is suspicious and should be blocked.
                _log_security_event(f"Blocked file command '{intent}': Path '{entity}' could not be safely resolved. Error: {e}")
                return (False, "Blocked: Invalid or non-resolvable path specified.")
        
        # If all checks pass, the command is considered safe.
        return (True, "Command is safe.")

# Singleton instance
_filter_instance = None

def get_security_filter():
    """Provides access to the singleton SecurityFilter instance."""
    global _filter_instance
    if _filter_instance is None:
        _filter_instance = SecurityFilter()
    return _filter_instance
