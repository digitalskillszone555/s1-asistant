# core/master_brain_v2.py
# S1 Assistant - Master Brain V2
# Focus: Orchestrating the new Action Intelligence System.

from nlp.command_expander import expand_command
from core.action_engine import get_action_engine
from core.brain import think # Fallback to legacy brain

class MasterBrainV2:
    """
    The central coordinator for all S1 intelligence.
    Connects NLP expansion, security checks, and final execution.
    """
    def __init__(self):
        self.action_engine = get_action_engine()

    def process(self, raw_text: str) -> str:
        """
        Main processing pipeline:
        Raw Text -> Expander -> Action Engine -> Result
        """
        if not raw_text:
            return "How can I help you today?"

        print(f"[MasterBrainV2] Input: '{raw_text}'")
        
        # 1. Expand the command (Rich NLP)
        intent_data = expand_command(raw_text)
        print(f"[MasterBrainV2] Intent Detected: {intent_data}")

        # 2. Execute the action (Action Engine)
        if intent_data.get("intent") != "unknown":
            response = self.action_engine.execute(intent_data)
            if response:
                return response

        # 3. Fallback to Legacy Brain (AI / Local logic)
        print("[MasterBrainV2] No specific action detected. Falling back to legacy brain.")
        legacy_reply, _ = think(raw_text)
        return legacy_reply

# Global Access
_master_v2_instance = MasterBrainV2()

def process_command_master(text: str):
    return _master_v2_instance.process(text)

# Test Runner
if __name__ == "__main__":
    import os, sys
    sys.path.append(os.getcwd())
    
    test_commands = [
        "open chrome",
        "search kittens",
        "youtube funny cats",
        "create file s1_test.txt",
        "write hello from s1 in s1_test.txt",
        "open file s1_test.txt"
    ]
    
    print("\n[MASTER BRAIN V2 TEST]")
    print("=" * 50)
    for cmd in test_commands:
        print(f"USER: {cmd}")
        res = process_command_master(cmd)
        print(f"S1  : {res}")
        print("-" * 50)
