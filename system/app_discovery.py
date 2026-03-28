# system/app_discovery.py
# S1 Assistant - App Discovery Engine
# Focus: Auto-detection of all installed applications on Windows.

import os
import json
import winreg
import platform
import shutil
from pathlib import Path

REGISTRY_PATH = "memory/app_registry.json"

class AppDiscoveryEngine:
    """
    Scans the system for installed applications and creates a mapping 
    of friendly names to executable paths.
    """
    def __init__(self):
        self.apps = {}
        self.is_windows = platform.system().lower() == "windows"

    def scan(self, force=False):
        """
        Scans the system and updates the registry. 
        Uses a cache to avoid slow startups unless 'force' is True.
        """
        if not self.is_windows:
            return {}

        # 1. Check Cache
        if not force and os.path.exists(REGISTRY_PATH):
            try:
                with open(REGISTRY_PATH, "r") as f:
                    self.apps = json.load(f)
                if self.apps:
                    print(f"[AppDiscovery] Loaded {len(self.apps)} apps from cache.")
                    return self.apps
            except Exception:
                pass

        print("[AppDiscovery] Starting deep system scan for apps...")
        self.apps = {}

        # 2. Scan Common Directories
        search_roots = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.path.join(os.environ.get("LocalAppData", ""), "Programs"),
        ]

        # 3. Scan Start Menu and Desktop Shortcuts (.lnk files)
        # Note: Parsing .lnk files properly requires 'pywin32' or 'pylnk'.
        # For this version, we will focus on direct executable discovery in common paths
        # and standard registry entries.

        for root_dir in search_roots:
            if not os.path.exists(root_dir):
                continue
            self._scan_directory(root_dir)

        # 4. Save to Cache
        os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
        with open(REGISTRY_PATH, "w") as f:
            json.dump(self.apps, f, indent=2)
        
        print(f"[AppDiscovery] Scan complete. Found {len(self.apps)} applications.")
        return self.apps

    def _scan_directory(self, base_path):
        """Shallow scan of directories to find main executables."""
        try:
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    # Look for .exe files directly inside the app folder
                    for file in os.listdir(item_path):
                        if file.lower().endswith(".exe"):
                            # Filter out uninstallers and helpers
                            if any(x in file.lower() for x in ["unins", "helper", "crash", "setup", "update"]):
                                continue
                            
                            app_name = item.lower()
                            # Store the first valid-looking exe as the primary
                            if app_name not in self.apps:
                                self.apps[app_name] = os.path.join(item_path, file)
        except PermissionError:
            pass
        except Exception as e:
            print(f"[AppDiscovery WARN] Error scanning {base_path}: {e}")

# Global Access
_discovery_instance = AppDiscoveryEngine()

def get_app_registry(force_refresh=False):
    return _discovery_instance.scan(force=force_refresh)

if __name__ == "__main__":
    # Test Scan
    registry = get_app_registry(force_refresh=True)
    for name, path in list(registry.items())[:10]:
        print(f"Detected: {name:20} -> {path}")
