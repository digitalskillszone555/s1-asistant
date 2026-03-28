# core/command_bridge.py
# S1 Assistant - Command Bridge V2
# Focus: Connecting NLP output to real-world execution.

from nlp.intent_engine_v2 import get_intent_v2
from core.execution_engine import run_command_v2

def process_command_v2(raw_text: str) -> str:
    """
    Complete V2 Pipeline: Raw Text -> NLP V2 -> Execution V2 -> Result Message.
    This bridge allows the assistant to handle commands and execute actions in one go.
    """
    if not raw_text or not isinstance(raw_text, str):
        return "Please tell me what you'd like me to do."

    # 1. NLP Phase (Standardizes text and extracts intent/entity)
    print(f"[BridgeV2] Processing: '{raw_text}'")
    intent_data = get_intent_v2(raw_text)
    
    intent = intent_data.get("intent")
    entity = intent_data.get("entity")
    
    print(f"[BridgeV2] NLP Result: intent='{intent}', entity='{entity}'")

    # 2. Execution Phase (Resolves app path and launches)
    if intent == "unknown":
        return "I'm sorry, I'm not sure how to help with that yet."
    
    result = run_command_v2(intent_data)
    
    return result

# --- Test Script for the entire pipeline ---
def test_pipeline():
    """Runs a series of tests to verify the entire pipeline (NLP -> EXEC)."""
    test_commands = [
        "open chrome",
        "notepad kholo",
        "launch calculator",
        "vscode chalao",
        "browser kholo"
    ]
    
    print("\n[PIPELINE V2 TEST] Starting end-to-end tests...")
    print("-" * 50)
    for cmd in test_commands:
        print(f"USER SAYS: {cmd}")
        response = process_command_v2(cmd)
        print(f"RESPONSE : {response}")
        print("-" * 50)

if __name__ == "__main__":
    test_pipeline()
