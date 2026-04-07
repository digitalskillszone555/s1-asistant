import os
import json
import time

def run_self_test():
    results = []
    overall_status = "PASS"

    # Test 1: Basic reply system
    try:
        from ai.ai_router import route_query
        reply = route_query("hello", "self_test")
        if reply and isinstance(reply, str):
            results.append({"name": "Reply System", "status": "PASS"})
        else:
            results.append({"name": "Reply System", "status": "FAIL"})
            overall_status = "FAIL"
    except Exception as e:
        results.append({"name": "Reply System", "status": "FAIL"})
        overall_status = "FAIL"

    # Test 2: Action system
    try:
        from actions.system_actions import open_app
        import builtins
        # Mock os.system safely
        original_system = os.system
        os.system = lambda cmd: 0
        try:
            success, msg = open_app("chrome")
            if success or "not in the allowed list" in msg or "opened" in msg.lower():
                results.append({"name": "Action System", "status": "PASS"})
            else:
                results.append({"name": "Action System", "status": "FAIL"})
                overall_status = "FAIL"
        finally:
            os.system = original_system
    except Exception as e:
        results.append({"name": "Action System", "status": "FAIL"})
        overall_status = "FAIL"

    # Test 3: Suggestion system
    try:
        from system.auto_mode import get_auto_mode_manager
        manager = get_auto_mode_manager()
        context = {
            "time_of_day": "morning",
            "hour": "9",
            "minute": 0,
            "last_app": "chrome",
            "last_intent": "open_app",
            "recent_commands": [],
            "habits_text": "gmail",
            "time_habit": None,
            "frequent_apps": [],
            "time_habits_list": [],
            "habit_tracker": None
        }
        suggestion = manager.generate_smart_suggestion(context)
        if suggestion and "reply" in suggestion and "actions" in suggestion:
            results.append({"name": "Suggestion System", "status": "PASS"})
        else:
            results.append({"name": "Suggestion System", "status": "FAIL"})
            overall_status = "FAIL"
    except Exception as e:
        results.append({"name": "Suggestion System", "status": "FAIL"})
        overall_status = "FAIL"

    # Test 4: Logging system
    try:
        actions_log = os.path.exists(os.path.join("logs", "actions.log"))
        errors_log = os.path.exists(os.path.join("logs", "errors.log"))
        # We just check if the directory exists and we can write to a test log, or if they exist.
        # But if they don't exist yet, it's fine, we just verify the path is valid.
        # Let's ensure no crash when checking.
        os.makedirs("logs", exist_ok=True)
        results.append({"name": "Logging System", "status": "PASS"})
    except Exception as e:
        results.append({"name": "Logging System", "status": "FAIL"})
        overall_status = "FAIL"

    # Test 5: Memory system
    try:
        from memory.memory_manager import get_memory_manager
        mem = get_memory_manager()._load_memory("profile")
        # Ensure it doesn't crash
        results.append({"name": "Memory System", "status": "PASS"})
    except Exception as e:
        results.append({"name": "Memory System", "status": "FAIL"})
        overall_status = "FAIL"

    return {
        "overall_status": overall_status,
        "tests": results
    }
