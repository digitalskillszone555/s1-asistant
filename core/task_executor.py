# core/task_executor.py
# S1 Assistant - Task Executor
# Focus: Sequentially executing planned steps and handling success/failure.

from core.action_engine import get_action_engine
from core.task_manager import get_task_manager

class TaskExecutor:
    """
    Executes a list of planned steps sequentially.
    """
    def __init__(self):
        self.action_engine = get_action_engine()
        self.task_manager = get_task_manager()

    def execute_plan(self, plan: list) -> str:
        """
        Executes each intent data in the plan list.
        Returns a combined response message.
        """
        if not plan:
            return "No task to execute."

        self.task_manager.start_task(plan)
        results = []

        for i, step in enumerate(plan):
            print(f"[TaskExecutor] Executing Step {i+1}: {step.get('raw_text')}")
            
            try:
                # Execute action using the existing ActionEngine
                response = self.action_engine.execute(step)
                
                # Check for failure based on common error phrases
                success = not ("error" in response.lower() or "blocked" in response.lower() or "failed" in response.lower())
                
                self.task_manager.update_step(i, success, response)
                results.append(response)

                if not success:
                    print(f"[TaskExecutor] Step {i+1} failed. Stopping task.")
                    break # Stop execution on failure for safety

            except Exception as e:
                print(f"[TaskExecutor ERROR] Unexpected error at step {i+1}: {e}")
                self.task_manager.update_step(i, False, f"Unexpected error: {e}")
                results.append(f"An unexpected error occurred at step {i+1}.")
                break

        # If all steps succeeded
        if self.task_manager.current_task["state"] != "FAILED":
            self.task_manager.complete_task()

        # Combine results into a final response
        return "\n".join(results)

# Global Access
_executor_instance = TaskExecutor()

def run_task_executor(plan: list) -> str:
    return _executor_instance.execute_plan(plan)
