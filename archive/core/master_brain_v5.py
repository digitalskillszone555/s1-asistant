# core/master_brain_v5.py
# S1 Assistant - Master Brain V5
# Focus: Autonomy, Self-Healing, Permissions, and Decision Making.

from nlp.multi_task_expander import get_multi_tasks
from core.task_planner import create_task_plan
from core.decision_engine import get_decision_engine
from core.action_engine import get_action_engine
from core.control_manager import get_control_manager
from core.autonomy_engine import get_autonomy_engine
from system.self_healing import get_self_healing
from memory.habit_tracker import get_habit_tracker
from interface_layer.interaction_manager import get_interaction_manager
from security.action_guard import get_action_guard

class MasterBrainV5:
    """
    The fully autonomous, self-healing, and permission-aware brain.
    """
    def __init__(self):
        self.decision_engine = get_decision_engine()
        self.action_engine = get_action_engine()
        self.control_manager = get_control_manager()
        self.autonomy_engine = get_autonomy_engine()
        self.self_healing = get_self_healing()
        self.habit_tracker = get_habit_tracker()
        self.interaction = get_interaction_manager()
        self.action_guard = get_action_guard()

        # State management for pending permissions
        self.pending_permissions = {} # session_id: { "intent_data": dict, "type": "ASK" | "DOUBLE_CONFIRM" }
        self.pending_autonomy = {} # session_id: suggestion_string

    def process(self, raw_text: str, session_id="default") -> str:
        """
        Main V5 pipeline.
        """
        if not raw_text:
            return "How can I help you today?"

        print(f"[MasterBrainV5] Processing: '{raw_text}'")

        # --- 1. Handle Pending Permissions ---
        if session_id in self.pending_permissions:
            return self._handle_pending_permission(raw_text, session_id)

        # --- 2. Handle Pending Autonomy Suggestions ---
        if session_id in self.pending_autonomy:
            # If the user says yes, we would ideally execute the suggestion.
            # For simplicity, we just clear it and acknowledge, or run a pre-canned intent.
            del self.pending_autonomy[session_id]
            if self.interaction.is_confirmed(raw_text):
                return "Okay, doing that now. (Simulated execution of suggestion)"
            elif self.interaction.is_denied(raw_text):
                return "Alright, moving on."
            # If they didn't explicitly say yes/no, we fall through and process as new command.

        # --- 3. Handle Pending Control Manager (V4 lifecycle: 'Keep it open?') ---
        feedback_res = self.control_manager.handle_user_feedback(raw_text, session_id)
        if feedback_res:
            print("[MasterBrainV5] Handled lifecycle feedback.")
            return feedback_res

        # --- 4. Process New Command ---
        tasks = get_multi_tasks(raw_text)
        plan = create_task_plan(tasks)
        
        results = []
        for step in plan:
            res = self._process_single_step(step, session_id)
            results.append(res)
            # If we hit a blocking state (asking permission), stop executing further steps for now.
            if session_id in self.pending_permissions:
                break
                
        return "\n".join(results)

    def _process_single_step(self, intent_data: dict, session_id: str) -> str:
        intent = intent_data.get("intent")
        entity = intent_data.get("entity")
        
        if intent == "unknown":
            return "I'm sorry, I couldn't understand that command."

        # --- A. Decision Engine (Execute, Ask, Refuse) ---
        decision = self.decision_engine.evaluate(intent_data)
        print(f"[MasterBrainV5] Decision for '{intent}': {decision}")

        if decision == "REFUSE":
            return f"I cannot perform '{intent}' for security reasons."
        elif decision == "ASK":
            self.pending_permissions[session_id] = {"intent_data": intent_data, "type": "ASK"}
            return f"This action ({intent}) requires your permission. Do you want to proceed?"

        # --- B. Action Guard Double Confirmation Check ---
        is_safe, msg = self.action_guard.is_action_safe(intent, entity, intent_data.get("extra_data"))
        if msg == "REQUIRES_DOUBLE_CONFIRM":
            self.pending_permissions[session_id] = {"intent_data": intent_data, "type": "DOUBLE_CONFIRM"}
            return f"WARNING: '{intent}' is a highly dangerous action. Are you absolutely sure?"
        elif not is_safe:
            return msg

        # --- C. Execution ---
        return self._execute_and_heal(intent_data, session_id)

    def _execute_and_heal(self, intent_data: dict, session_id: str) -> str:
        """Executes the action, attempts self-healing if failed, and triggers autonomy."""
        intent = intent_data.get("intent")
        entity = intent_data.get("entity")

        try:
            response = self.action_engine.execute(intent_data)
        except Exception as e:
            response = f"Execution failed: {e}"

        # Detect failure based on response text
        is_failure = any(kw in response.lower() for kw in ["failed", "couldn't find", "blocked", "error"])

        # --- D. Self-Healing ---
        if is_failure:
            healed_response = self.self_healing.handle_failure(intent_data, response)
            if healed_response:
                return healed_response
            return response # Return original error if no healing possible

        # --- E. Record Habit (Implicit approval if we got here without asking) ---
        self.habit_tracker.record_decision(intent, True)

        # --- F. Lifecycle Check (Control Manager) ---
        response = self.control_manager.handle_task_result(intent_data, response, session_id)

        # --- G. Autonomy Suggestion ---
        suggestion = self.autonomy_engine.get_suggestion(intent, entity)
        if suggestion and session_id not in self.control_manager.pending_decisions:
            self.pending_autonomy[session_id] = suggestion
            response += f"\n{suggestion}"

        return response

    def _handle_pending_permission(self, user_input: str, session_id: str) -> str:
        pending = self.pending_permissions.pop(session_id)
        intent_data = pending["intent_data"]
        intent = intent_data.get("intent")

        if self.interaction.is_confirmed(user_input):
            print(f"[MasterBrainV5] Permission GRANTED for '{intent}'.")
            self.habit_tracker.record_decision(intent, True)
            
            # Since permission was granted, bypass the initial Decision Engine check
            # and move directly to Action Guard check and Execution.
            
            entity = intent_data.get("entity")
            
            # --- Action Guard Double Confirmation Check ---
            is_safe, msg = self.action_guard.is_action_safe(intent, entity, intent_data.get("extra_data"))
            
            if pending["type"] == "ASK" and msg == "REQUIRES_DOUBLE_CONFIRM":
                # If it was just a standard ask, but the guard says it's super dangerous
                self.pending_permissions[session_id] = {"intent_data": intent_data, "type": "DOUBLE_CONFIRM"}
                return f"WARNING: '{intent}' is a highly dangerous action. Are you absolutely sure?"
            elif pending["type"] == "DOUBLE_CONFIRM" or is_safe:
                # Permission is fully granted, or it's a double confirm that we just confirmed
                return self._execute_and_heal(intent_data, session_id)
            else:
                return msg

        else:
            print(f"[MasterBrainV5] Permission DENIED for '{intent}'.")
            self.habit_tracker.record_decision(intent, False)
            return "Action cancelled."


# Global Access
_master_v5_instance = MasterBrainV5()

def process_command_master_v5(text: str, session_id="default"):
    return _master_v5_instance.process(text, session_id)
