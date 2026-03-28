# system/health_check.py
import os
import sys
from utils.logging_utils import log_event

def run_health_check(config: dict) -> (bool, dict):
    """
    Checks the status of critical system modules.
    Returns: (success: bool, report: dict)
    """
    report = {
        "core": "UNKNOWN",
        "nlp": "UNKNOWN",
        "memory": "UNKNOWN",
        "voice": "UNKNOWN",
        "ai": "UNKNOWN"
    }
    
    overall_success = True

    # 1. Check Core
    try:
        from core.master_brain_v7 import process_command_master_v7
        report["core"] = "OK"
    except Exception as e:
        report["core"] = f"ERROR: {e}"
        overall_success = False

    # 2. Check NLP
    try:
        from nlp.intent_engine_v2 import get_intent_v2
        report["nlp"] = "OK"
    except Exception as e:
        report["nlp"] = f"ERROR: {e}"
        overall_success = False

    # 3. Check Memory
    try:
        from memory.memory_manager import get_memory_manager
        get_memory_manager()
        report["memory"] = "OK"
    except Exception as e:
        report["memory"] = f"ERROR: {e}"
        overall_success = False

    # 4. Check Voice (if enabled)
    if config.get("voice_enabled"):
        try:
            import speech_recognition as sr
            import pyttsx3
            report["voice"] = "OK"
        except Exception as e:
            report["voice"] = f"WARN: {e}"
            # Voice failure might not be fatal for the whole system
    else:
        report["voice"] = "DISABLED"

    # 5. Check AI
    try:
        from ai.ai_engine import get_ai_engine
        report["ai"] = "OK"
    except Exception as e:
        report["ai"] = f"ERROR: {e}"
        overall_success = False

    log_event("HEALTH_CHECK", f"System Health: {'SUCCESS' if overall_success else 'FAILED'}", report=report)
    return overall_success, report
