import sys
import os
import traceback

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from core.master_brain_v7 import process_command_master_v7

TEST_COMMANDS = [
    # Calculator
    "calculator kholo",
    "open calculator",
    "calculator open",

    # Notepad
    "notepad kholo",
    "close notepad",
    "band karo notepad",

    # Time
    "samay koto",
    "samay bolo",
    "time now",
    "what time",

    # Chrome
    "chrome kholo",
    "open chrome",
    "বন্ধ কর chrome",

    # User system
    "new user create Rahul",
    "switch user Rahul",
    "amar naam set koro Rahul",

    # Memory system
    "remember that I like coding",
    "what do you remember about me",
    "forget this",
    "clear my memory",

    # Mode system
    "activate office mode",
    "sleep mode on",

    # Language
    "set language bangla",
    "set language english",

    # Exit tests (should NOT break loop)
    "exit",
    "turn off",
    "বন্ধ কর",
]

print("\n" + "="*10 + " S1 AUTOMATED CORE TEST START " + "="*10 + "\n")

for i, cmd in enumerate(TEST_COMMANDS, start=1):
    try:
        print(f"[{i}] TEST INPUT: {cmd}")

        reply = process_command_master_v7(cmd)
        should_exit = False # Unified brain doesn't explicitly return exit flag

        print(f"[REPLY]: {reply}")
        print(f"[EXIT FLAG]: {should_exit}")

        # Prevent test runner from stopping even if exit command is detected
        if should_exit:
            print("[INFO] Exit intent detected, but continuing test loop safely.")

    except Exception as e:
        print("[ERROR] Exception occurred during test!")
        print(str(e))
        traceback.print_exc()

    print("-" * 60)

print("\n" + "="*10 + " TEST END " + "="*10 + "\n")
