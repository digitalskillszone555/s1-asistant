# memory/memory_manager.py

import os
import json
import time
import base64

from system.config_loader import load_config, save_config
from utils.logging_utils import log_event

# --- Cryptography Imports ---
try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("[WARN] Cryptography package not found. Memory encryption is DISABLED.")


# --- Encryption Key Generator ---


def _get_encryption_key():
    if not CRYPTOGRAPHY_AVAILABLE:
        return None

    config = load_config() or {}

    secret = config.get("encryption_secret")
    salt = config.get("encryption_salt")

    config_updated = False

    if not secret:
        log_event("ENCRYPTION", "Generating new encryption secret")
        secret = base64.urlsafe_b64encode(os.urandom(32)).decode()
        config["encryption_secret"] = secret
        config_updated = True

    if not salt:
        log_event("ENCRYPTION", "Generating new encryption salt")
        salt = base64.urlsafe_b64encode(os.urandom(16)).decode()
        config["encryption_salt"] = salt
        config_updated = True

    if config_updated:
        save_config(config)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=base64.urlsafe_b64decode(salt.encode()),
        iterations=480000,
    )

    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))


# --- Encryption Engine ---


class EncryptionEngine:
    def __init__(self, key):
        self.key = key
        self.fernet = Fernet(key) if key else None

    def encrypt(self, data: bytes):
        if not self.fernet:
            return data
        return self.fernet.encrypt(data)

    def decrypt(self, token: bytes):
        if not self.fernet:
            return token

        try:
            return self.fernet.decrypt(token)

        except InvalidToken:
            log_event("ENCRYPTION", "Invalid encryption token")
            return None

        except Exception as e:
            log_event("ENCRYPTION", f"Decrypt error: {e}")
            return None


# --- Memory Manager ---


class MemoryManager:
    def __init__(self):

        self.memory_types = ["profile", "habits", "facts"]

        self.encryption_engine = EncryptionEngine(_get_encryption_key())

        self.limits = {
            "free": {"facts": 200, "habits": 50, "profile": 50},
            "pro": {"facts": 5000, "habits": 1000, "profile": 1000},
        }

        if not CRYPTOGRAPHY_AVAILABLE:
            log_event(
                "MEMORY_MANAGER",
                "Cryptography not installed. Memory stored in plaintext",
            )
        else:
            log_event("MEMORY_MANAGER", "Memory encryption enabled")


    # --- Memory File Path ---

    def _get_user_memory_file(self, mem_type: str):

        if mem_type not in self.memory_types:
            return None

        user_memory_path = "memory_data"

        os.makedirs(user_memory_path, exist_ok=True)

        file_path = os.path.join(user_memory_path, f"{mem_type}.json")

        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(self.encryption_engine.encrypt(b"{}"))

        return file_path


    # --- Load Memory ---


    def _load_memory(self, mem_type: str):

        file_path = self._get_user_memory_file(mem_type)

        if not file_path:
            return {}

        try:

            with open(file_path, "rb") as f:
                encrypted_data = f.read()

            if not encrypted_data:
                return {}

            decrypted = self.encryption_engine.decrypt(encrypted_data)

            if decrypted is not None:
                return json.loads(decrypted)

            log_event("MIGRATION", f"Attempting plaintext migration for {file_path}")

            try:

                plaintext = json.loads(encrypted_data.decode())

                self._save_memory(mem_type, plaintext)

                log_event("MIGRATION", "Migration successful")

                return plaintext

            except Exception:
                log_event("ERROR", "Memory file corrupted")

                return {}

        except Exception as e:

            log_event("ERROR", f"Memory read failed: {e}")

            return {}


    # --- Save Memory ---


    def _save_memory(self, mem_type: str, data: dict):

        file_path = self._get_user_memory_file(mem_type)

        if not file_path:
            return False

        json_bytes = json.dumps(data, indent=4).encode()

        encrypted = self.encryption_engine.encrypt(json_bytes)

        with open(file_path, "wb") as f:
            f.write(encrypted)

        return True


    # --- Public API ---


    def save_memory(self, mem_type: str, key: str, value):

        if mem_type not in self.memory_types:
            return False

        data = self._load_memory(mem_type)

        data[key] = {"value": value, "timestamp": time.time()}

        user_info = {"plan": "free"}

        current_plan = user_info.get("plan", "free")

        limit = self.limits.get(current_plan, {}).get(mem_type, 0)

        if len(data) > limit:

            oldest_key = min(data, key=lambda k: data[k].get("timestamp", 0))

            del data[oldest_key]

            log_event(
                "QUOTA",
                f"Memory limit reached ({limit}). Removed oldest entry '{oldest_key}'",
            )

        return self._save_memory(mem_type, data)


    def get_memory(self, mem_type: str, key: str):

        data = self._load_memory(mem_type)

        if data and key in data:
            return data[key].get("value")

        return None


    def delete_memory(self, mem_type: str, key: str):

        data = self._load_memory(mem_type)

        if data and key in data:
            del data[key]

            return self._save_memory(mem_type, data)

        return False


    def list_memory(self, mem_type: str):

        data = self._load_memory(mem_type)

        if not data:
            return []

        return [item.get("value") for item in data.values() if "value" in item]


# --- Global Instance ---


S1_MEMORY = MemoryManager()


def get_memory_manager():
    return S1_MEMORY# --- Migration Utilities ---

def migrate_v1_to_v2(username: str):
    """
    Migrates data from the encrypted MemoryManager (v1) 
    to the offline-first MemoryEngineV2 (v2).
    """
    from memory.memory_engine_v2 import get_memory_engine_v2
    
    v1 = get_memory_manager()
    v2 = get_memory_engine_v2()
    
    log_event("MIGRATION", f"Starting migration for user: {username}")
    
    # Migrate Facts
    facts_data = v1._load_memory("facts")
    for key, entry in facts_data.items():
        v2.save_fact(username, key, entry.get("value"))
        
    # Migrate Preferences (from profile)
    profile_data = v1._load_memory("profile")
    for key, entry in profile_data.items():
        v2.save_preference(username, key, entry.get("value"))
        
    # Migrate Habits
    habits_data = v1._load_memory("habits")
    for key, entry in habits_data.items():
        # V1 habits were key-value, V2 uses track_habit logic. 
        # We'll manually inject the counts.
        current_habits = v2._read_user_data(username, "habits")
        if "command_counts" not in current_habits:
            current_habits["command_counts"] = {}
        
        current_habits["command_counts"][key] = entry.get("value", 1)
        v2._write_user_data(username, "habits", current_habits)

    log_event("MIGRATION", f"Migration to V2 complete for {username}")
    return True
    