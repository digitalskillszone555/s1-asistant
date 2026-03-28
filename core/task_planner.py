# core/task_planner.py
# S1 Assistant - Task Planner
# Focus: Converting a list of command strings into a structured plan of intents.

from nlp.command_expander import expand_command
from nlp.followup_resolver import get_followup_resolver

class TaskPlanner:
    """
    Takes a list of individual commands and generates a sequence of 
    structured intent dictionaries.
    """
    def __init__(self):
        self.followup = get_followup_resolver()

    def plan(self, tasks: list) -> list:
        """
        Input: ["open chrome", "search cats"]
        Output: [ {intent: open_app, ...}, {intent: search_web, ...} ]
        """
        if not tasks:
            return []

        print(f"[TaskPlanner] Planning {len(tasks)} steps...")
        plan_steps = []

        for task_text in tasks:
            # 1. Get initial structured intent
            intent_data = expand_command(task_text)
            
            # 2. Apply context resolution (Follow-up logic)
            resolved_intent, confidence = self.followup.resolve(intent_data)
            if confidence >= 0.7:
                intent_data = resolved_intent
            
            # If a task cannot be mapped to an action, mark it as unknown
            if not intent_data or intent_data.get("intent") == "unknown":
                print(f"[TaskPlanner WARN] Step could not be resolved: '{task_text}'")
            
            # Add the original text for logging purposes
            intent_data["raw_text"] = task_text
            plan_steps.append(intent_data)

        return plan_steps

# Global Access
_planner_instance = TaskPlanner()

def create_task_plan(tasks: list) -> list:
    return _planner_instance.plan(tasks)
