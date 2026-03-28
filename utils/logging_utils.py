# utils/logging_utils.py
import os
from datetime import datetime
from typing import Any, Dict

LOG_DIRECTORY = "logs"
DEFAULT_LOG_FILE = "assistant.log"

def log_event(log_type: str, message: str, level: str = "INFO", log_file: str = DEFAULT_LOG_FILE, **kwargs: Any):
    """
    Centralized logging utility for the S1 Assistant.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build a context string from kwargs
    context_parts = []
    for key, value in kwargs.items():
        if value is not None:
            context_parts.append(f"{key.capitalize()}:'{value}'")
    context_string = " ".join(context_parts)
    if context_string:
        context_string = f" ({context_string})"

    log_entry = f"[{timestamp}] [{level}] [{log_type}] {message}{context_string}\n"
    
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    full_path = os.path.join(LOG_DIRECTORY, log_file)
    try:
        with open(full_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"[ERROR] Failed to write to log file {full_path}: {e}")
