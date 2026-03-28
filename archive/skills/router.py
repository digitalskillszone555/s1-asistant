# skills/router.py
# New, modular skills router.

from skills.app_control import AppControlSkill
from skills.system_control import SystemControlSkill
from skills.file_control import FileControlSkill
from skills.web_control import WebControlSkill
from skills.security_filter import get_security_filter
from user.user_manager import get_user_manager
from security.permissions import can_execute
from security.hardening import get_security_hardener
from utils.logging_utils import log_event # Centralized logging

# --- Existing Legacy Skills ---
# These need to be imported or re-registered
from skills import time, date, weather, system_info

# --- Configuration ---
SKILL_CONFIDENCE_THRESHOLD = 0.6 # Minimum confidence required for skill execution.

class SkillsRouter:
    """
    The central router that directs intents to the appropriate skill.
    It maintains a registry of all available skills and queries them
    to find one that can handle a given intent.
    """
    def __init__(self):
        self.skills = []
        self._register_skills()
        self.hardener = get_security_hardener()

        # Perform system integrity check at startup
        self.hardener.check_integrity()

    def _register_skills(self):
        """Initializes and registers all available skill classes."""
        self.skills.append(AppControlSkill())
        self.skills.append(SystemControlSkill())
        self.skills.append(FileControlSkill())
        self.skills.append(WebControlSkill())
        log_event("SKILL_ROUTER", f"Registered {len(self.skills)} modular skills.")
        
        self.legacy_skills = {
            "time": time.run,
            "date": date.run,
            "weather": weather.run,
            "system_info": system_info.run
        }
        log_event("SKILL_ROUTER", f"Registered {len(self.legacy_skills)} legacy skills.")


    def route(self, intent: str, entity: str, confidence: float = 1.0, **kwargs) -> str:
        """
        Routes an intent to the correct skill, with confidence, permission, security, hardening, and logging layers.
        """
        username = get_user_manager().current_user
        user_info = get_user_manager().get_current_user_info()
        user_role = user_info.get("role", "user")

        # --- Hardening Layer 1: Command Rate Limiting ---
        is_rate_limited, msg = self.hardener.check_rate_limit(username, intent)
        if not is_rate_limited:
            self.hardener.update_trust_score(username, "RATE_LIMIT_EXCEEDED", intent=intent, entity=entity)
            log_event("SKILL_ROUTER", msg, log_type="RATE_LIMITED", username=username, intent=intent)
            return msg

        # --- Hardening Layer 2: Trust Score Check ---
        is_trusted, msg = self.hardener.check_trust_score(username)
        if not is_trusted:
            log_event("SKILL_ROUTER", msg, log_type="TRUST_SCORE_BLOCK", username=username)
            return msg

        # --- Hardening Layer 3: Confidence Threshold Check ---
        if confidence < SKILL_CONFIDENCE_THRESHOLD:
            self.hardener.update_trust_score(username, "LOW_CONFIDENCE", intent=intent, entity=entity)
            log_event("SKILL_ROUTER", f"Confidence ({confidence:.2f}) below threshold ({SKILL_CONFIDENCE_THRESHOLD:.2f}). Triggering fallback.", 
                      log_type="LOW_CONFIDENCE_FALLBACK", username=username, intent=intent, confidence=confidence)
            return "NLP_LOW_CONFIDENCE_FALLBACK"

        # --- Core Security Layer 1: Permission Check ---
        if not can_execute(intent, user_role):
            self.hardener.update_trust_score(username, "PERMISSION_DENIED", intent=intent, entity=entity)
            log_event("SKILL_ROUTER", "Permission denied for role to execute intent.", 
                      log_type="PERMISSION_DENIED", username=username, role=user_role, intent=intent)
            return "You do not have permission to perform this action."

        # --- Core Security Layer 2: Security Filter ---
        security_filter = get_security_filter()
        is_safe, message = security_filter.is_safe(intent, entity, **kwargs)
        if not is_safe:
            self.hardener.update_trust_score(username, "SECURITY_BLOCKED", intent=intent, entity=entity)
            log_event("SKILL_ROUTER", f"Security filter blocked: {message}", 
                      log_type="SECURITY_BLOCKED", username=username, intent=intent, entity=entity)
            return message

        # --- Hardening Layer 4: Replay Protection (for critical commands) ---
        is_not_replay, msg = self.hardener.check_command_replay(username, intent, entity)
        if not is_not_replay:
            self.hardener.update_trust_score(username, "REPLAY_BLOCKED", intent=intent, entity=entity)
            log_event("SKILL_ROUTER", msg, log_type="REPLAY_BLOCKED", username=username, intent=intent, entity=entity)
            return msg

        # --- Skill Routing and Execution ---
        try:
            reply = None
            # First, check modular class-based skills
            for skill in self.skills:
                if intent in skill.supported_intents:
                    log_event("SKILL_ROUTER", f"Routing intent '{intent}' to modular skill '{skill.name}'.", intent=intent, skill=skill.name)
                    reply = skill.execute(intent, entity, **kwargs)
                    break

            # Second, check legacy functional skills if not handled by modular skills
            if reply is None and intent in self.legacy_skills:
                log_event("SKILL_ROUTER", f"Routing intent '{intent}' to legacy skill.", intent=intent)
                reply = self.legacy_skills[intent]()
            
            if reply:
                self.hardener.update_trust_score(username, "VALID_COMMAND", intent=intent, entity=entity)
                log_event("SKILL_ROUTER", "Skill executed successfully.", log_type="SUCCESS", username=username, intent=intent)
                return reply
            else:
                self.hardener.update_trust_score(username, "NOT_FOUND", intent=intent, entity=entity)
                log_event("SKILL_ROUTER", "No skill found to handle intent.", log_type="NOT_FOUND", username=username, intent=intent)
                return None

        except Exception as e:
            self.hardener.update_trust_score(username, "EXECUTION_ERROR", intent=intent, entity=entity)
            log_event("SKILL_ROUTER", f"Skill execution failed: {e}", log_type="EXECUTION_ERROR", username=username, intent=intent, error=str(e))
            return "An error occurred while trying to perform this action."

# Singleton instance of the router
_router_instance = None

def get_skills_router():
    """Provides access to the singleton SkillsRouter instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = SkillsRouter()
    return _router_instance

# Global function for core/brain.py to call for simplicity
def route_skill(intent: str, entity: str, confidence: float = 1.0, **kwargs) -> str:
    """
    Convenience function to access the router's route method,
    now including confidence.
    """
    return get_skills_router().route(intent, entity, confidence, **kwargs)