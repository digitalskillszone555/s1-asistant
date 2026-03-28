# skills/file_actions.py
# S1 Assistant - File Action Module
# Focus: Safe file creation, writing, and opening.

import os
from pathlib import Path
import platform
import subprocess

class FileActions:
    """
    Handles local file system tasks safely.
    Restricts operations to a controlled workspace directory for safety.
    """
    def __init__(self, workspace_dir="workspace"):
        self.workspace = Path(workspace_dir)
        if not self.workspace.exists():
            self.workspace.mkdir(parents=True, exist_ok=True)

    def _get_safe_path(self, filename: str) -> Path:
        """Ensures the file stays within the workspace and is a safe path."""
        # Normalize name and remove directory traversal attempts
        safe_name = os.path.basename(filename)
        return self.workspace / safe_name

    def create_file(self, filename: str) -> str:
        """Creates an empty file if it doesn't already exist."""
        if not filename:
            return "Please provide a file name."
        
        target_path = self._get_safe_path(filename)
        if target_path.exists():
            return f"The file '{filename}' already exists."

        target_path.touch()
        return f"Successfully created '{filename}' in the workspace."

    def write_file(self, filename: str, content: str) -> str:
        """Writes content to a file. Appends by default for safety."""
        if not filename:
            return "Please provide a file name."
        
        target_path = self._get_safe_path(filename)
        try:
            with open(target_path, "a", encoding="utf-8") as f:
                f.write(f"{content}\n")
            return f"Written content to '{filename}'."
        except Exception as e:
            print(f"[FileActions ERROR] Write failed: {e}")
            return f"Sorry, I couldn't write to '{filename}'."

    def open_file(self, filename: str) -> str:
        """Opens the specified file using the system's default handler."""
        if not filename:
            return "Please provide a file name."
        
        target_path = self._get_safe_path(filename)
        if not target_path.exists():
            return f"I couldn't find the file '{filename}'."

        try:
            if platform.system().lower() == "windows":
                os.startfile(target_path)
            else:
                opener = "open" if platform.system().lower() == "darwin" else "xdg-open"
                subprocess.Popen([opener, str(target_path)])
            return f"Opening '{filename}'..."
        except Exception as e:
            print(f"[FileActions ERROR] Open failed: {e}")
            return f"Sorry, I couldn't open the file '{filename}'."

# Global Access
_file_actions_instance = FileActions()

def get_file_actions():
    return _file_actions_instance
