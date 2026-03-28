# skills/app_resolver_v2.py
# S1 Assistant - Smart App Resolver V2
# Focus: Dynamic discovery of installed applications on Windows.

import os
import shutil
import platform

class AppResolverV2:
    """
    Advanced resolver that locates executables by searching common installation
    directories and the system PATH.
    """
    def __init__(self):
        self.is_windows = platform.system().lower() == "windows"
        
        # Common App Alias -> Executable Name Mapping
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
        Resolves an app alias to a full executable path.
        Returns: Path string or None.
        """
        if not alias:
            return None

        alias = alias.lower()
        exec_names = self.app_map.get(alias, [f"{alias}.exe", alias])

        for name in exec_names:
            # 1. Check System PATH (Fastest)
            path = shutil.which(name)
            if path:
                return path

            # 2. Deep Search in common directories (Windows only)
            if self.is_windows:
                for base_dir in self.search_dirs:
                    if not os.path.exists(base_dir):
                        continue
                    
                    # Optimization: Look for direct matches in the base_dir first
                    direct_path = os.path.join(base_dir, name)
                    if os.path.exists(direct_path):
                        return direct_path

                    # Deep search (limited depth for performance)
                    # Note: Full os.walk can be slow, we'll try a shallow scan first
                    try:
                        for root, dirs, files in os.walk(base_dir):
                            if name in files:
                                return os.path.join(root, name)
                            # Limit depth to avoid freezing on massive drives
                            if root.count(os.sep) - base_dir.count(os.sep) > 2:
                                del dirs[:] # Don't go deeper
                    except PermissionError:
                        continue

        return None

# Singleton instance
_resolver_instance = None

def get_resolver_v2():
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = AppResolverV2()
    return _resolver_instance

# Test Function
if __name__ == "__main__":
    resolver = get_resolver_v2()
    test_apps = ["chrome", "notepad", "vscode", "explorer"]
    print("[ResolverV2 Test]")
    for app in test_apps:
        path = resolver.resolve(app)
        print(f"ALIAS: {app:10} | PATH: {path}")
