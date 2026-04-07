# skills/app_resolver_v3.py
# S1 Assistant - App Resolver V3
# Focus: Unified lookup combining manual rules (V2) and auto-discovery (V3).

import os
import shutil
import platform
from system.app_matcher import find_app_path

class AppResolverV3:
    """
    Advanced resolver that locates executables by searching common installation
    directories, system PATH, and dynamic discovery.
    """
    def __init__(self):
        self.is_windows = platform.system().lower() == "windows"
        
        # Common App Alias -> Executable Name Mapping (Legacy V2 logic)
        self.app_map = {
            "chrome": ["chrome.exe", "google-chrome"],
            "browser": ["chrome.exe", "msedge.exe", "firefox.exe"],
            "notepad": ["notepad.exe"],
            "editor": ["code.exe", "notepad.exe", "sublime_text.exe"],
            "vscode": ["code.exe"],
            "code": ["code.exe"],
            "edge": ["msedge.exe"],
            "firefox": ["firefox.exe"],
            "calculator": ["calc.exe"],
            "vlc": ["vlc.exe"],
            "discord": ["Discord.exe"],
            "spotify": ["Spotify.exe"],
            "explorer": ["explorer.exe"]
        }

        # Directories to search if shutil.which fails
        self.search_dirs = []
        if self.is_windows:
            self.search_dirs = [
                os.environ.get("ProgramFiles", "C:\\Program Files"),
                os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
                os.path.join(os.environ.get("LocalAppData", ""), "Google\\Chrome\\Application"),
                os.path.join(os.environ.get("LocalAppData", ""), "Programs\\Microsoft VS Code"),
                os.path.join(os.environ.get("LocalAppData", ""), "Microsoft\\WindowsApps"),
            ]

    def resolve(self, alias: str) -> str:
        """
        1. Try manual V2 logic (Mapping & System PATH)
        2. Fallback to V3 dynamic discovery (most comprehensive)
        """
        if not alias:
            return None

        alias = alias.lower()

        # --- STEP 1: Legacy V2 Logic (Fast PATH check & Common Mapping) ---
        exec_names = self.app_map.get(alias, [f"{alias}.exe", alias])

        for name in exec_names:
            # Check System PATH
            path = shutil.which(name)
            if path:
                return path

            # Deep Search in common directories (Windows only)
            if self.is_windows:
                for base_dir in self.search_dirs:
                    if not os.path.exists(base_dir):
                        continue
                    
                    direct_path = os.path.join(base_dir, name)
                    if os.path.exists(direct_path):
                        return direct_path

                    try:
                        for root, dirs, files in os.walk(base_dir):
                            if name in files:
                                return os.path.join(root, name)
                            if root.count(os.sep) - base_dir.count(os.sep) > 2:
                                del dirs[:] 
                    except PermissionError:
                        continue

        # --- STEP 2: V3 (Dynamic App Registry) ---
        path = find_app_path(alias)
        if path:
            print(f"[ResolverV3] Resolved via V3 Dynamic Discovery: '{alias}' -> {path}")
            return path

        return None

# Global Access
_resolver_v3_instance = None

def get_resolver_v3():
    global _resolver_v3_instance
    if _resolver_v3_instance is None:
        _resolver_v3_instance = AppResolverV3()
    return _resolver_v3_instance
