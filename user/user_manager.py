# user/user_manager.py

import os
import json
import shutil

import os
import json
import shutil
from typing import Dict, Any
from security.permissions import ADMIN_ROLE, USER_ROLE
from memory.memory_manager import EncryptionEngine, _get_encryption_key, CRYPTOGRAPHY_AVAILABLE
from utils.logging_utils import log_event # Centralized logging

class UserManager:
    def __init__(self, base_memory_path="memory"):
        self.base_memory_path = base_memory_path
        self.users_file = os.path.join(self.base_memory_path, "users.json")
        self.encryption_engine = EncryptionEngine(_get_encryption_key())
        self.users_data = self._load_users_data()
        
        if not CRYPTOGRAPHY_AVAILABLE:
            log_event("USER_MANAGER", "Cryptography package not installed. users.json will be handled in plaintext.", level="WARNING")
            print("[CRITICAL SECURITY WARNING] users.json is NOT ENCRYPTED.") # Keep print for critical visibility
        else:
            log_event("USER_MANAGER", "users.json encryption is ENABLED.")
        
        if not self.users_data.get("users"):
            log_event("USER_MANAGER", "No users found. Creating 'default' user.")
            self.create_user("default", is_initial_setup=True)
            self._set_active_user("default")
        
        self.current_user = self.users_data.get("last_active_user", "default")
        log_event("USER_MANAGER", f"UserManager initialized. Current user: '{self.current_user}'")

    def _load_users_data(self):
        """Loads the main users.json file, handling encryption/decryption and migration."""
        if not os.path.exists(self.users_file):
            log_event("USER_MANAGER", f"users.json not found at {self.users_file}.")
            return {"last_active_user": None, "users": {}}
        
        file_data_bytes = b''
        try:
            with open(self.users_file, 'rb') as f:
                file_data_bytes = f.read()
            if not file_data_bytes:
                return {"last_active_user": None, "users": {}}
        except IOError as e:
            log_event("USER_MANAGER", f"IOError reading users.json: {e}")
            return {"last_active_user": None, "users": {}}

        decrypted_data_bytes = None
        if CRYPTOGRAPHY_AVAILABLE:
            decrypted_data_bytes = self.encryption_engine.decrypt(file_data_bytes)

        if decrypted_data_bytes is not None: # Decryption successful
            try:
                data = json.loads(decrypted_data_bytes)
                log_event("USER_MANAGER", "users.json loaded successfully (encrypted).")
                return self._ensure_user_roles(data)
            except json.JSONDecodeError as e:
                log_event("USER_MANAGER", f"JSONDecodeError after decrypting users.json: {e}. File might be corrupt or old encrypted.")
        
        # If decryption failed or CRYPTOGRAPHY_AVAILABLE is False, try as plaintext (migration path)
        log_event("USER_MANAGER", f"Decryption failed or not available for users.json. Attempting as plaintext (migration).")
        try:
            plaintext_data = json.loads(file_data_bytes.decode('utf-8'))
            log_event("USER_MANAGER", "users.json loaded successfully as plaintext. Migrating to encrypted format.")
            data = self._ensure_user_roles(plaintext_data)
            self._save_users_data(data) # Immediately re-save to encrypt it
            return data
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            log_event("CRITICAL", f"users.json is neither valid encrypted data nor valid plaintext JSON: {e}.")
            return {"last_active_user": None, "users": {}}

    def _ensure_user_roles(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures all loaded users have a role, defaulting to USER_ROLE."""
        if "users" in data:
            for username, user_info in data["users"].items():
                if "role" not in user_info:
                    user_info["role"] = USER_ROLE
                    log_event("USER_MANAGER", f"Assigned default role '{USER_ROLE}' to user '{username}'.")
        return data

    def _save_users_data(self, data: Dict[str, Any] = None):
        """Saves the main users.json file, encrypting it if cryptography is available."""
        data_to_save = data if data is not None else self.users_data
        
        json_data_bytes = json.dumps(data_to_save, indent=4).encode('utf-8')

        if CRYPTOGRAPHY_AVAILABLE:
            encrypted_data = self.encryption_engine.encrypt(json_data_bytes)
            mode = 'wb'
            content = encrypted_data
            log_event("USER_MANAGER", "users.json saved successfully (encrypted).")
        else:
            mode = 'w'
            content = json_data_bytes.decode('utf-8')
            log_event("USER_MANAGER", "users.json saved successfully (plaintext). Cryptography not available.")

        try:
            with open(self.users_file, mode) as f:
                f.write(content)
        except IOError as e:
            log_event("USER_MANAGER", f"IOError saving users.json: {e}")

    def _set_active_user(self, username: str):
        """
        Internal-only method to set the active user without security checks.
        Used for system startup and safe fallbacks.
        """
        self.current_user = username
        self.users_data["last_active_user"] = username
        self._save_users_data()
        log_event("USER_MANAGER", f"System set active user to '{username}'.")

    def create_user(self, username: str, plan="free", is_initial_setup=False):
        """
        Creates a new user with the default 'user' role.
        Requires the current user to be an ADMIN, unless it's the initial setup.
        """
        if not is_initial_setup:
            current_user_info = self.get_current_user_info()
            if not current_user_info or current_user_info.get("role") != ADMIN_ROLE:
                log_event("SECURITY", f"USER_CREATION DENIED: User '{self.current_user}' (Role: {current_user_info.get('role')}) attempted to create new user '{username}'. ADMIN role required.", level="WARNING", log_file="security.log")
                return False, "Permission denied. Administrator role required to create users."
        
        if username in self.users_data["users"]:
            return False, f"User '{username}' already exists."
        
        # New users are always created with the default USER_ROLE for security.
        self.users_data["users"][username] = {"plan": plan, "role": USER_ROLE}
        self._save_users_data()
        
        user_memory_path = self.get_user_memory_path(username)
        if not os.path.exists(user_memory_path):
            os.makedirs(user_memory_path)
        
        log_event("USER_MANAGER", f"Created user '{username}' with plan '{plan}' and role '{USER_ROLE}'.")
        return True, f"User '{username}' created successfully."

    def switch_user(self, username: str):
        """
        Switches the active user. Only allows switching to a different user
        if the current user has the ADMIN role.
        """
        if username not in self.users_data["users"]:
            return False, f"User '{username}' not found."
            
        current_user_info = self.get_current_user_info()
        
        # Allow if the user is switching to themselves (no-op)
        if self.current_user == username:
            return True, f"User is already '{username}'."

        # Block if a non-admin tries to switch to someone else
        if not current_user_info or current_user_info.get("role") != ADMIN_ROLE:
            log_event("SECURITY", f"USER_SWITCH DENIED: User '{self.current_user}' (Role: {current_user_info.get('role')}) attempted to switch to user '{username}'. ADMIN role required.", level="WARNING", log_file="security.log")
            return False, "Permission denied. Administrator role required to switch to another user."

        self._set_active_user(username)
        return True, f"Switched to user '{username}'."

    def delete_user(self, username: str):
        """
        Deletes a user and all their data. Requires ADMIN role.
        """
        current_user_info = self.get_current_user_info()
        if not current_user_info or current_user_info.get("role") != ADMIN_ROLE:
            log_event("SECURITY", f"USER_DELETION DENIED: User '{self.current_user}' (Role: {current_user_info.get('role')}) attempted to delete user '{username}'. ADMIN role required.", level="WARNING", log_file="security.log")
            return False, "Permission denied. Administrator role required to delete users."

        if username not in self.users_data["users"]:
            return False, f"User '{username}' not found."
        if username == "default":
            return False, "Cannot delete the default user."
        
        del self.users_data["users"][username]
        
        if self.users_data["last_active_user"] == username:
            self._set_active_user("default")
        
        self._save_users_data()
        
        user_memory_path = self.get_user_memory_path(username)
        if os.path.exists(user_memory_path):
            shutil.rmtree(user_memory_path)
            
        log_event("USER_MANAGER", f"Deleted user '{username}'.")
        log_event("SECURITY", f"USER_DELETED: Admin '{self.current_user}' successfully deleted user '{username}'.", level="INFO", log_file="security.log")
        return True, f"User '{username}' has been deleted."

    def list_users(self):
        """Returns a list of all existing usernames."""
        return list(self.users_data["users"].keys())

    def get_current_user_info(self):
        """Returns the profile of the current active user, including role."""
        if self.current_user:
            user_info = self.users_data["users"].get(self.current_user)
            if user_info and "role" not in user_info:
                user_info["role"] = USER_ROLE # Ensure role is always present
            return user_info
        return None

    def get_user_memory_path(self, username: str):
        """Constructs the memory path for a given user."""
        return os.path.join(self.base_memory_path, username)

    def get_current_user_memory_path(self):
        """Returns the memory path of the current active user."""
        return self.get_user_memory_path(self.current_user)

# Global user manager instance
S1_USER_MANAGER = UserManager()

def get_user_manager():
    return S1_USER_MANAGER

