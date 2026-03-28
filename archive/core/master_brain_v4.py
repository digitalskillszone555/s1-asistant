# core/master_brain_v4.py
# S1 Assistant - Master Brain V4
# Focus: Integrating Task Control, Completion, and Multi-Step Logic.

from nlp.multi_task_expander import get_multi_tasks
from core.task_planner import create_task_plan
from core.task_executor import run_task_executor
from core.control_manager import get_control_manager
from core.master_brain_v3 import process_command_master_v3 # Fallback

class MasterBrainV4:
    """
    The advanced brain with task control and lifecycle management.
    """
    def __init__(self):
        self.control_manager = get_control_manager()

    def process(self, raw_text: str) -> str:
        """
        Main V4 pipeline:
        1. Handle follow-up decisions (Yes/No)
        2. Execute new commands
        3. Check completion and ask for further actions
        """
        if not raw_text:
            return "How can I help you today?"

        # 1. First check if we're waiting for user feedback from a previous task
        feedback_res = self.control_manager.handle_user_feedback(raw_text)
        if feedback_res:
            print("[MasterBrainV4] User feedback processed.")
            return feedback_res

        # 2. Otherwise, treat as a new command (reusing V3 logic for planning/exec)
        print(f"[MasterBrainV4] Processing: '{raw_text}'")
        
        # Step A: Detection & Planning
        tasks = get_multi_tasks(raw_text)
        
        # We need the intent_data for the *last* task to check if we should ask follow-up questions
        # (This is a simplified approach; in a full system we'd check all steps)
        plan = create_task_plan(tasks)
        
        # Step B: Sequential Execution
        response = run_task_executor(plan)
        
        # Step C: Post-task Lifecycle Logic (Asking to close apps, etc.)
        if len(plan) > 0:
            last_intent_data = plan[-1]
            # Wrap the original response with lifecycle questions if needed
            response = self.control_manager.handle_task_result(last_intent_data, response)

        return response

# Global Access
_master_v4_instance = MasterBrainV4()

def process_command_master_v4(text: str):
    return _master_v4_instance.process(text)

# Test Script
if __name__ == "__main__":
    import os, sys
    sys.path.append(os.getcwd())

    # Mock user-assistant interaction
    print("\n[MASTER BRAIN V4 TEST]")
    print("=" * 60)
    
    # CASE 1: Open an app and then decide to close it
    print("USER: open chrome")
    res1 = process_command_master_v4("open chrome")
    print(f"S1  : {res1}")
    
    print("\nUSER: no close it")
    res2 = process_command_master_v4("no close it")
    print(f"S1  : {res2}")
    print("-" * 60)

    # CASE 2: Multi-tasking then keeping an app open
    print("USER: search cats then open notepad")
    res3 = process_command_master_v4("search cats then open notepad")
    print(f"S1  : {res3}")
    
    print("\nUSER: yes keep it open")
    res4 = process_command_master_v4("yes keep it open")
    print(f"S1  : {res4}")
    print("-" * 60)
