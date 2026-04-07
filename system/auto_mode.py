import threading
import time
import json
import os
from datetime import datetime
from utils.logging_utils import log_event
from utils.state import get_state_manager, AssistantState
from memory.conversation_memory import get_conversation_memory
from memory.habit_tracker import get_habit_tracker
from memory.memory_engine import get_memory_engine
from system.config import AUTO_EXECUTION_ENABLED, DEBUG_MODE
from security.whitelist import SAFE_AUTO_ACTIONS

SAFE_WHITELIST = ["chrome", "notepad", "calc"]

class AutoModeManager:
    def __init__(self):
        self.enabled = False
        self.auto_execution = AUTO_EXECUTION
        self.running = False
        self.thread = None
        self.last_suggestion = None
        self.suggestion_queue = []
        self.state_manager = get_state_manager()

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            log_event("AUTO_MODE", "Background Auto Mode Started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        log_event("AUTO_MODE", "Background Auto Mode Stopped")

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        log_event("AUTO_MODE", f"Auto Mode set to {'ENABLED' if enabled else 'DISABLED'}")

    def set_auto_execution(self, enabled: bool):
        self.auto_execution = enabled
        log_event("AUTO_MODE", f"Auto Execution set to {'ENABLED' if enabled else 'DISABLED'}")

    def get_latest_suggestion(self):
        if self.suggestion_queue:
            return self.suggestion_queue.pop(0)
        return None

    def _run_loop(self):
        while self.running:
            try:
                if self.enabled:
                    # Check context and generate suggestions
                    suggestion = self._analyze_context()
                    if suggestion and suggestion != self.last_suggestion:
                        self.suggestion_queue.append(suggestion)
                        self.last_suggestion = suggestion
                        log_event("AUTO_MODE", f"New suggestion: {suggestion['reply']}")
                
                # Sleep for 15 seconds as per requirements (10-20s)
                time.sleep(15)
            except Exception as e:
                log_event("AUTO_MODE", f"Error in loop: {e}", level="ERROR")
                time.sleep(15)

    def _get_time_of_day(self, hour: int) -> str:
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _analyze_context(self):
        """Analyzes time and habits to suggest actions using the Smart Decision Layer."""
        # Only suggest if assistant is IDLE (No user conflict)
        if self.state_manager.get_state() != AssistantState.IDLE:
            return None

        now = datetime.now()
        
        # Use MemoryEngine for intelligent data
        memory_engine = get_memory_engine()
        habits_text = memory_engine.get_memory_summary().lower()
        frequent_apps = memory_engine.get_frequent_apps()
        time_habits_list = memory_engine.get_time_based_habits()

        # Use HabitTracker for strong time patterns (already has THRESHOLD=3)
        habit_tracker = get_habit_tracker()
        time_habit = habit_tracker.get_time_of_day_habit()

        conv_memory = get_conversation_memory()
        recent_history = conv_memory.history[-3:] if conv_memory.history else []
        recent_commands = [turn.get("user", "") for turn in recent_history]
        last_app = conv_memory.get_last_app()
        last_intent = conv_memory.get_last_intent()

        context = {
            "time_of_day": self._get_time_of_day(now.hour),
            "hour": str(now.hour),
            "minute": now.minute,
            "last_app": last_app,
            "last_intent": last_intent,
            "recent_commands": recent_commands,
            "habits_text": habits_text,
            "time_habit": time_habit,
            "frequent_apps": frequent_apps,
            "time_habits_list": time_habits_list,
            "habit_tracker": habit_tracker
        }

        return self.generate_smart_suggestion(context)

    def generate_smart_suggestion(self, context: dict):
        """Generates the best suggestion using multi-condition logic and scoring."""
        suggestions = []
        
        time_of_day = context["time_of_day"]
        last_app = context["last_app"]
        habits_text = context["habits_text"]
        time_habit = context["time_habit"]
        recent_commands = context["recent_commands"]
        frequent_apps = context["frequent_apps"]
        time_habits_list = context["time_habits_list"]
        habit_tracker = context["habit_tracker"]

        # Rule 1: Sequential Habit (Chrome -> Gmail)
        if last_app == "chrome" and "gmail" in habits_text:
            suggestions.append({
                "score": 90,
                "reply": "You usually check Gmail after opening Chrome. Want me to open it?",
                "actions": [{"type": "open_url", "data": "https://mail.google.com"}],
                "reason": "Based on your habit of checking Gmail after opening Chrome"
            })

        # Rule 2: Strong Time-of-Day Habit from HabitTracker
        if time_habit:
            intent = time_habit.get("intent")
            entity = time_habit.get("entity")
            freq = time_habit.get("freq", 0)
            if intent == "open_app" and entity:
                suggestions.append({
                    "score": 88,
                    "reply": f"It's about time you usually open {entity}. Want me to do it for you?",
                    "actions": [{"type": "open_app", "data": entity}],
                    "reason": f"Based on your daily habit of opening {entity} around this time",
                    "freq": freq
                })

        # Rule 3: Intelligent Time-Based Habits from MemoryEngine
        current_time_habit = f"{time_of_day} = "
        for h in time_habits_list:
            if h.startswith(current_time_habit):
                app_name = h.split(" = ")[1]
                suggestions.append({
                    "score": 85,
                    "reply": f"Since it's {time_of_day}, would you like to open {app_name}?",
                    "actions": [{"type": "open_app", "data": app_name}],
                    "reason": f"Based on your {time_of_day} routine of using {app_name}"
                })

        # Rule 4: Frequent Apps Priority
        if not suggestions and frequent_apps and not recent_commands:
            best_app = frequent_apps[0]
            suggestions.append({
                "score": 60,
                "reply": f"You use {best_app} quite often. Want to open it now?",
                "actions": [{"type": "open_app", "data": best_app}],
                "reason": f"Based on your frequent usage of {best_app}"
            })

        # Rule 5: Sequential Habit (Notepad -> Reminder)
        if last_app == "notepad":
            suggestions.append({
                "score": 85,
                "reply": "You just opened Notepad. Should I set a reminder to check your notes later?",
                "actions": [{"type": "speak", "data": "Reminder feature pending implementation."}],
                "reason": "Based on your habit of taking notes"
            })

        # Rule 6: Morning Setup (Time + Habit)
        is_work_habit = any(w in habits_text for w in ["work", "workspace", "code", "project", "study"])
        if time_of_day == "morning" and (is_work_habit or "chrome" in habits_text) and not recent_commands:
            suggestions.append({
                "score": 80,
                "reply": "Good morning! Ready to set up your workspace?",
                "actions": [
                    { "type": "open_url", "data": "https://calendar.google.com" },
                    { "type": "open_url", "data": "https://gmail.com" }
                ],
                "reason": "Based on your morning work routine"
            })

        # Rule 7: Resume Work (Idle + Work Habit)
        if time_of_day in ["morning", "afternoon"] and is_work_habit and not recent_commands:
            suggestions.append({
                "score": 75,
                "reply": "You seem to be in work mode. Should I help you resume your recent tasks?",
                "actions": [],
                "reason": "Based on your ongoing work tasks"
            })

        # Rule 8: Night Idle (Time + Activity)
        if time_of_day == "night" and not recent_commands:
            suggestions.append({
                "score": 70,
                "reply": "It's getting late and you seem idle. Should we call it a day and wind down?",
                "actions": [],
                "reason": "Based on your late night inactivity"
            })

        # Rule 9: Generic Fallback (low priority)
        if not suggestions and not recent_commands:
            if time_of_day == "morning":
                suggestions.append({
                    "score": 40,
                    "reply": "Good morning! Anything I can help with to start your day?",
                    "actions": [],
                    "reason": "Standard morning greeting"
                })
            elif time_of_day == "night":
                 suggestions.append({
                    "score": 40,
                    "reply": "Good evening! Still working or ready to wind down?",
                    "actions": [],
                    "reason": "Standard evening greeting"
                })

        if not suggestions:
            return None

        # Sort by score descending
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        best_suggestion = suggestions[0]
        
        # --- Controlled Smart Auto Execution (Phase 2) ---
        auto_execute = False
        if self.auto_execution:
            score = best_suggestion.get("score", 0)
            actions = best_suggestion.get("actions", [])
            
            # Check Safe Conditions:
            # 1. Score >= 90
            # 2. Whitelist Check (chrome, notepad, calc)
            # 3. Repeated habit (>= 5 times)
            
            is_whitelisted = True
            for a in actions:
                if a.get("type") == "open_app":
                    if a.get("data") not in SAFE_WHITELIST:
                        is_whitelisted = False
                        break
                else:
                    # For now, only whitelisted apps are auto-executable
                    is_whitelisted = False
                    break
            
            # Get freq for habit check
            freq = best_suggestion.get("freq", 0)
            if not freq and actions:
                # Calculate freq if not provided
                a = actions[0]
                if a.get("type") == "open_app":
                    key = f"open_app:{a.get('data')}"
                    patterns = habit_tracker.time_patterns.get(key, {})
                    freq = sum(patterns.values()) # Total count

            if score >= 90 and is_whitelisted and freq >= 5:
                auto_execute = True
                log_event("AUTO_MODE", f"Auto-executing suggestion: {best_suggestion['reply']} (Score: {score}, Freq: {freq})")

        return {
            "reply": best_suggestion["reply"],
            "actions": best_suggestion["actions"],
            "requires_confirmation": not auto_execute,
            "auto_execute": auto_execute,
            "reason": best_suggestion.get("reason", "N/A")
        }


# Singleton instance
_auto_mode_manager = AutoModeManager()

def get_auto_mode_manager():
    return _auto_mode_manager

