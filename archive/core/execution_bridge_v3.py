# core/execution_bridge_v3.py
# S1 Assistant - Execution Bridge V3
# Focus: Connecting V2 NLP to V3 Smart Execution.

from nlp.intent_engine_v2 import get_intent_v2
from skills.app_resolver_v3 import get_resolver_v3
import subprocess
import os

class ExecutionBridgeV3:
    """
    Main entry point for command execution using the new V3 Discovery System.
    """
    def __init__(self):
        self.resolver_v3 = get_resolver_v3()

    def process_and_execute(self, raw_text: str) -> str:
        """
        1. NLP (Intent + Entity)
        2. Resolve (V3 Discovery)
        3. Execute
        """
        if not raw_text:
            return "Please tell me what you'd like me to do."

        # STEP 1: NLP
        print(f"[BridgeV3] Processing: '{raw_text}'")
        intent_data = get_intent_v2(raw_text)
        intent = intent_data.get("intent")
        entity = intent_data.get("entity")

        if intent == "unknown":
            return "I'm sorry, I'm not sure how to help with that yet."

        # STEP 2: Resolve (V3 is the star here)
        if intent == "open_app":
            if not entity:
                return "Which application would you like me to open?"
            
            app_path = self.resolver_v3.resolve(entity)
            if not app_path:
                return f"I couldn't find '{entity}' on your system."

            # STEP 3: Execute
            try:
                subprocess.Popen(app_path, shell=True)
                return f"Opening {entity}..."
            except Exception as e:
                print(f"[BridgeV3 ERROR] Launch failed: {e}")
                return f"Sorry, I found {entity} but couldn't open it."

        # Default fallback for other intents (not handled in this bridge)
        return f"Intent '{intent}' is not yet optimized for V3 Bridge."

# Global Access
_bridge_v3_instance = None

def execute_command_v3(text: str):
    global _bridge_v3_instance
    if _bridge_v3_instance is None:
        _bridge_v3_instance = ExecutionBridgeV3()
    return _bridge_v3_instance.process_and_execute(text)

# Test Runner
if __name__ == "__main__":
    import os
    # Ensure current directory is in sys.path to find 'nlp'
    import sys
    sys.path.append(os.getcwd())
    
    test_cases = ["open chrome", "open notepad", "open vs code", "spotify chalao"]
    print("[ExecutionBridgeV3 Test]")
    for tc in test_cases:
        response = execute_command_v3(tc)
        print(f"INPUT: {tc:15} | RESPONSE: {response}")
