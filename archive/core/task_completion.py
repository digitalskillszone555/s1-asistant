# core/task_completion.py
# S1 Assistant - Task Completion Detector
# Focus: Determining the outcome of an action based on its intent.

from system.app_state import get_app_state

class TaskCompletionDetector:
    """
    Analyzes intent outcomes to check if a task is effectively finished.
    """
    def __init__(self):
        self.app_state = get_app_state()

    def check(self, intent_data: dict, result_message: str) -> dict:
        """
        Determines the status of a task after execution.
        Returns: { "status": "completed" | "running" | "failed", "confidence": float }
        """
        intent = intent_data.get("intent")
        entity = intent_data.get("entity")
        
        # 1. Failure Detection (Common patterns in result messages)
        fail_triggers = ["couldn't find", "failed", "error", "blocked", "not sure"]
        if any(trigger in result_message.lower() for trigger in fail_triggers):
            return {"status": "failed", "confidence": 1.0}

        # 2. Intent-specific check
        
        # OPEN APP: Status is "running" if the app is active
        if intent == "open_app":
            # If we just launched it, it might still be in startup
            return {"status": "running", "confidence": 0.8}

        # WEB SEARCH: Usually instant once the browser is opened
        if intent in ["search_web", "search_youtube", "open_url"]:
            return {"status": "completed", "confidence": 0.9}

        # FILE OPERATIONS: Usually instant
        if intent in ["create_file", "write_file", "open_file"]:
            return {"status": "completed", "confidence": 1.0}

        # Default fallback
        return {"status": "completed", "confidence": 0.5}

# Global Access
_completion_instance = TaskCompletionDetector()

def check_task_completion(intent_data: dict, result_message: str):
    return _completion_instance.check(intent_data, result_message)
