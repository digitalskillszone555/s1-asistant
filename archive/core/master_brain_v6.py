# core/master_brain_v6.py
# S1 Assistant - Master Brain V6
# Focus: Integrating Natural Control, Context Awareness, and Lifecycle Management.

from nlp.control_intent import parse_control_intent
from core.context_manager_v2 import get_context_v2
from core.master_brain_v5 import process_command_master_v5
from core.action_engine import get_action_engine

class MasterBrainV6:
    """
    The brain with natural language control and context-aware targeting.
    """
    def __init__(self):
        self.context = get_context_v2()
        self.action_engine = get_action_engine()

    def process(self, raw_text: str, session_id="default") -> str:
        """
        Main V6 pipeline:
        1. Parse for control intents (close, minimize, switch)
        2. Resolve ambiguous targets (it/this) via context
        3. Execute or fallback to V5 brain
        """
        if not raw_text:
            return "How can I help you?"

        print(f"[MasterBrainV6] Processing: '{raw_text}'")

        # --- A. Natural Control Check ---
        control_data = parse_control_intent(raw_text)
        
        if control_data:
            intent = control_data["intent"]
            target = control_data["target"]
            
            # Resolve context-aware targeting ("it" -> "last_app")
            resolved_target = self.context.resolve_target(target)
            
            print(f"[MasterBrainV6] Control Action: {intent} ON {resolved_target}")
            
            if resolved_target == "it":
                return "I'm not sure which app you mean. Please specify the name."

            # Map the intent for execution
            intent_data = {
                "intent": intent,
                "entity": resolved_target
            }
            
            return self.action_engine.execute(intent_data)

        # --- B. Standard Flow (V5: Intent -> Decision -> Autonomy) ---
        response = process_command_master_v5(raw_text, session_id)
        
        # --- C. Post-processing: Update context if an app was successfully opened ---
        # (This is a simplified way to capture 'last_app' context)
        if "Opening" in response:
            # Try to extract the app name from the original text for more accuracy
            from nlp.intent_engine_v2 import get_intent_v2
            intent_data = get_intent_v2(raw_text)
            if intent_data["intent"] == "open_app":
                self.context.update_context(intent_data["entity"], "open_app")

        return response

# Global Access
_master_v6_instance = MasterBrainV6()

def process_command_master_v6(text: str, session_id="default"):
    return _master_v6_instance.process(text, session_id)

# Test Script
if __name__ == "__main__":
    import os, sys
    sys.path.append(os.getcwd())
    
    # Mocking flow
    print("\n[MASTER BRAIN V6 TEST]")
    print("=" * 60)
    
    # CASE 1: Open and then close with context "it"
    print("USER: open chrome")
    res1 = process_command_master_v6("open chrome")
    print(f"S1  : {res1}")
    
    print("\nUSER: close it")
    res2 = process_command_master_v6("close it")
    print(f"S1  : {res2}")
    print("-" * 60)
    
    # CASE 2: Native Bengali command
    print("USER: open notepad")
    res3 = process_command_master_v6("open notepad")
    print(f"S1  : {res3}")
    
    print("\nUSER: বন্ধ করো")
    res4 = process_command_master_v6("বন্ধ করো")
    print(f"S1  : {res4}")
    print("-" * 60)
    
    # CASE 3: Banglish command with specific name
    print("USER: browser kete dao")
    res5 = process_command_master_v6("browser kete dao")
    print(f"S1  : {res5}")
    print("-" * 60)
