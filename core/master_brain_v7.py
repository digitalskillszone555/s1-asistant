# core/master_brain_v7.py
# S1 Assistant - Master Brain V7 (CONFIRMATION & CONTROL)
# Focus: Risk-aware execution with previews, confirmation, and undo.

import time
import threading
from nlp.multi_task_expander import get_multi_tasks
from nlp.control_intent import parse_control_intent
from nlp.followup_resolver import get_followup_resolver
from nlp.intent_engine_v2 import get_intent_v2
from nlp.emotion_detector import detect_emotion
from core.task_planner import create_task_plan
from core.task_executor import run_task_executor
from core.response_engine import get_response_engine
from core.decision_engine import get_decision_engine
from core.action_engine import get_action_engine
from core.control_manager import get_control_manager
from core.autonomy_engine import get_autonomy_engine
from core.context_manager_v2 import get_context_v2
from system.self_healing import get_self_healing
from system.ai_mode_manager import get_ai_mode_manager
from system.mode_manager import get_mode_manager
from system.config_loader import load_config
from memory.conversation_memory import get_conversation_memory
from memory.habit_tracker import get_habit_tracker
from memory.memory_engine import get_memory_engine
from interface_layer.interaction_manager import get_interaction_manager
from security.action_guard import get_action_guard
from ai.ai_router import get_ai_response
from language.language_manager import get_language_manager
from analytics.studio_reporter import send_event
from utils.cleaner import clean_command

class MasterBrainV7:
    def __init__(self):
        self.memory = get_conversation_memory()
        self.response_engine = get_response_engine()
        self.followup = get_followup_resolver()
        self.context = get_context_v2()
        self.decision_engine = get_decision_engine()
        self.action_engine = get_action_engine()
        self.control_manager = get_control_manager()
        self.autonomy_engine = get_autonomy_engine()
        self.self_healing = get_self_healing()
        self.habit_tracker = get_habit_tracker()
        self.interaction = get_interaction_manager()
        self.action_guard = get_action_guard()
        self.memory_engine = get_memory_engine()
        self.lang_manager = get_language_manager()
        
        self.pending_permissions = {} 
        self.pending_autonomy = {}
        self.last_executed_intent = None # For Undo

    def process(self, raw_text: str, session_id="default") -> str:
        if not raw_text:
            return self.response_engine.generate({"intent": "greeting"}, emotion="happy")

        print(f"[MasterBrainV7] Input: '{raw_text}'")
        
        # 0. Emotion & Memory
        current_emotion = detect_emotion(raw_text)
        self.context.update_context(None, None, emotion=current_emotion)
        emotional_trend = self.context.get_emotional_trend()
        self.memory_engine.analyze_and_memorize(raw_text, None)

        # 1. Handle Pendings
        if session_id in self.pending_permissions:
            return self._handle_permission(raw_text, session_id)
        if session_id in self.pending_autonomy:
            suggestion_res = self._handle_autonomy_feedback(raw_text, session_id)
            if suggestion_res: return suggestion_res
        
        # 2. Handle Undo Command
        if any(w in raw_text.lower() for w in ["undo", "revert", "back"]):
            return self._handle_undo(session_id)

        # 3. Standard Logic
        tasks = get_multi_tasks(raw_text)
        plan = create_task_plan(tasks)
        
        if plan:
            # Resolve Context
            resolved_intent, confidence = self.followup.resolve(plan[0])
            if confidence >= 0.7: plan[0] = resolved_intent

            # Execute Multi-step
            results = []
            last_success = True
            for step in plan:
                res = self._process_step(step, session_id)
                results.append(res)
                if session_id in self.pending_permissions: break
                if "failed" in res.lower() or "error" in res.lower(): last_success = False
            
            final_raw_res = "\n".join(results)
            human_res = self.response_engine.generate(plan[0], success=last_success, emotion=emotional_trend)
            
            # Carry extra logic info
            if "(" in final_raw_res:
                human_res += f" ({final_raw_res.split('(', 1)[1]}"
            elif "[BUTTONS]" in final_raw_res:
                human_res += f" {final_raw_res[final_raw_res.find('[BUTTONS]'):]}"

            self.memory.add_turn(raw_text, human_res, plan[0])
            return human_res

        # 4. AI Fallback
        ai_response = get_ai_response(raw_text)
        if ai_response: return ai_response

        return self.response_engine.generate({"intent": "unknown"}, emotion=emotional_trend)

    def _process_step(self, intent_data: dict, session_id: str) -> str:
        intent = intent_data.get("intent")
        if intent == "unknown": return "I'm not sure how to do that."

        # Decision with Preview & Confirmation
        decision = self.decision_engine.evaluate(intent_data)
        
        if decision == "REFUSE": return "I cannot do that for security reasons."
        
        if decision == "ASK":
            preview = self.decision_engine.get_preview_text(intent_data)
            self.pending_permissions[session_id] = {"intent_data": intent_data, "type": "ASK"}
            return f"{preview} Do you want me to proceed? [BUTTONS: Yes, No]"

        return self._execute_and_heal(intent_data, session_id)

    def _execute_and_heal(self, intent_data: dict, session_id: str) -> str:
        try:
            response = self.action_engine.execute(intent_data)
            # Store for Undo if successful
            if "opening" in response.lower() or "created" in response.lower():
                self.last_executed_intent = intent_data
                response += " [BUTTONS: Undo]"
        except Exception as e:
            response = f"Error: {e}"

        # Self-Healing & Autonomy
        if "failed" in response.lower():
            healed = self.self_healing.handle_failure(intent_data, response)
            if healed: return healed

        self.habit_tracker.record_decision(intent_data.get("intent"), True, entity=intent_data.get("entity"))
        return self.control_manager.handle_task_result(intent_data, response, session_id)

    def _handle_undo(self, session_id):
        if not self.last_executed_intent:
            return "There is nothing to undo."
        
        last = self.last_executed_intent
        self.last_executed_intent = None # Clear it
        
        if last["intent"] == "open_app":
            undo_intent = {"intent": "close_app", "entity": last["entity"]}
            res = self.action_engine.execute(undo_intent)
            return f"Alright, I've undone that by closing {last['entity']}."
        
        if last["intent"] == "create_file":
            return f"I've created the file, but I cannot delete it automatically for safety. You can delete it manually if needed."

        return "I'm sorry, I don't know how to undo that specific action yet."

    def _handle_permission(self, text, session_id):
        pending = self.pending_permissions.pop(session_id)
        if self.interaction.is_confirmed(text):
            return self._execute_and_heal(pending["intent_data"], session_id)
        return "Okay, I've cancelled that action."

    def _handle_autonomy_feedback(self, text, session_id):
        # ... existing logic ...
        return None

# Global Instance
_brain = MasterBrainV7()

def process_command_master_v7(text: str, session_id="default"):
    return _brain.process(text, session_id)
