# core/task_manager.py
# S1 Assistant - Task Manager
# Focus: Managing task state and persistent memory.

import json
import os
from datetime import datetime

STATE_FILE = "memory/task_state.json"

class TaskManager:
    """
    Tracks the lifecycle of a task and manages persistence.
    States: "IDLE", "RUNNING", "COMPLETED", "FAILED"
    """
    def __init__(self):
        self.current_task = {
            "id": None,
            "state": "IDLE",
            "steps": [],
            "completed_steps": [],
            "failed_steps": [],
            "start_time": None
        }
        self.load_state()

    def start_task(self, steps: list):
        """Initializes a new task tracking state."""
        self.current_task = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "state": "RUNNING",
            "steps": steps,
            "completed_steps": [],
            "failed_steps": [],
            "start_time": str(datetime.now())
        }
        self.save_state()
        print(f"[TaskManager] Task '{self.current_task['id']}' started with {len(steps)} steps.")

    def update_step(self, index: int, success: bool, message: str):
        """Records the outcome of a step."""
        if not self.current_task["id"]:
            return

        step_info = {
            "index": index,
            "result": message,
            "timestamp": str(datetime.now())
        }

        if success:
            self.current_task["completed_steps"].append(step_info)
        else:
            self.current_task["failed_steps"].append(step_info)
            self.current_task["state"] = "FAILED"
        
        self.save_state()

    def complete_task(self):
        """Marks the entire task as successfully completed."""
        self.current_task["state"] = "COMPLETED"
        self.save_state()
        print(f"[TaskManager] Task '{self.current_task['id']}' completed.")

    def save_state(self):
        """Persists the task state to memory."""
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.current_task, f, indent=4)
        except Exception as e:
            print(f"[TaskManager ERROR] Failed to save state: {e}")

    def load_state(self):
        """Loads the last saved task state."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    self.current_task = json.load(f)
            except Exception:
                pass

# Global Access
_manager_instance = TaskManager()

def get_task_manager():
    return _manager_instance
