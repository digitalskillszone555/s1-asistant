# core/master_brain_v3.py
# S1 Assistant - Master Brain V3
# Focus: Orchestrating Multi-Step Task Execution.

from nlp.multi_task_expander import get_multi_tasks
from core.task_planner import create_task_plan
from core.task_executor import run_task_executor
from core.master_brain_v2 import process_command_master # Fallback for single-step logic

class MasterBrainV3:
    """
    The advanced brain of S1 that supports complex, multi-step tasks.
    """
    def process(self, raw_text: str) -> str:
        """
        Main multi-step pipeline:
        Raw Text -> MultiTaskExpander -> TaskPlanner -> TaskExecutor
        """
        if not raw_text:
            return "How can I help you?"

        # 1. Detect multiple tasks (Split by "and", "then", etc.)
        tasks = get_multi_tasks(raw_text)

        # 2. If it's only one task, fallback to the existing V2 brain
        if len(tasks) <= 1:
            print("[MasterBrainV3] Single-step command detected. Using V2 logic.")
            return process_command_master(raw_text)

        # 3. Multi-Step Flow
        print(f"[MasterBrainV3] Multi-step task detected: {tasks}")
        
        # Step A: Planning
        plan = create_task_plan(tasks)
        
        # Step B: Execution
        response = run_task_executor(plan)
        
        return response

# Global Access
_master_v3_instance = MasterBrainV3()

def process_command_master_v3(text: str):
    return _master_v3_instance.process(text)

# Test Script
if __name__ == "__main__":
    import os, sys
    sys.path.append(os.getcwd())

    test_commands = [
        "open chrome and search kittens",
        "create file multi_test.txt then write multi-step success in multi_test.txt",
        "open youtube and search funny cats",
        "open calculator" # Single step fallback test
    ]

    print("\n[MASTER BRAIN V3 TEST]")
    print("=" * 60)
    for cmd in test_commands:
        print(f"USER: {cmd}")
        res = process_command_master_v3(cmd)
        print(f"S1  :\n{res}")
        print("-" * 60)
