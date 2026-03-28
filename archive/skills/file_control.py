# skills/file_control.py
import os
import shutil
from skills.base_skill import BaseSkill

class FileControlSkill(BaseSkill):
    """
    Skill for performing basic file system operations.
    Relies on the SecurityFilter for path validation.
    """
    def __init__(self):
        super().__init__("FileControl", ["open_file", "delete_file", "move_file", "list_directory"])

    def execute(self, intent: str, entity: str, **kwargs) -> str:
        if intent == "open_file":
            return self._open_file(entity)
        elif intent == "delete_file":
            return self._delete_file(entity)
        elif intent == "move_file":
            src = entity # entity is source
            dest = kwargs.get("dest") # destination from kwargs
            if not dest:
                return "Error: Destination not specified for move operation."
            return self._move_file(src, dest)
        elif intent == "list_directory":
            return self._list_directory(entity)
        else:
            return f"File control intent '{intent}' not recognized."

    def _open_file(self, path: str) -> str:
        """Opens a file using the default associated application."""
        if not os.path.exists(path):
            return f"Error: File or directory '{path}' not found."
        
        try:
            # os.startfile is Windows-specific. subprocess.Popen might work cross-platform.
            if sys.platform == "win32":
                os.startfile(path)
                return f"Opening '{path}'."
            elif sys.platform == "darwin": # macOS
                subprocess.run(["open", path])
                return f"Opening '{path}'."
            elif sys.platform == "linux": # Linux
                subprocess.run(["xdg-open", path])
                return f"Opening '{path}'."
            else:
                return f"File opening not supported on this OS: '{path}'."

        except Exception as e:
            return f"Error opening '{path}': {e}"

    def _delete_file(self, path: str) -> str:
        """Deletes a file or an empty directory."""
        if not os.path.exists(path):
            return f"Error: File or directory '{path}' not found."
        
        try:
            if os.path.isfile(path):
                os.remove(path)
                return f"Deleted file '{path}'."
            elif os.path.isdir(path):
                # Only delete empty directories for safety
                os.rmdir(path) 
                return f"Deleted empty directory '{path}'."
            else:
                return f"Error: '{path}' is neither a file nor an empty directory."
        except OSError as e:
            return f"Error deleting '{path}': {e}"

    def _move_file(self, src: str, dest: str) -> str:
        """Moves a file or directory from source to destination."""
        if not os.path.exists(src):
            return f"Error: Source '{src}' not found."
        
        try:
            shutil.move(src, dest)
            return f"Moved '{src}' to '{dest}'."
        except shutil.Error as e:
            return f"Error moving '{src}' to '{dest}': {e}"
        except OSError as e:
            return f"Error moving '{src}' to '{dest}': {e}"

    def _list_directory(self, path: str) -> str:
        """Lists the contents of a directory."""
        if not os.path.isdir(path):
            return f"Error: Directory '{path}' not found."
        
        try:
            contents = os.listdir(path)
            return f"Contents of '{path}': {', '.join(contents)}"
        except OSError as e:
            return f"Error listing directory '{path}': {e}"