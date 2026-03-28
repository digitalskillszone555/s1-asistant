# test_master_brain_v3.py
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from core.master_brain_v7 import process_command_master_v7

test_commands = [
    "open chrome and search kittens",
    "create file multi_test.txt then write multi-step success in multi_test.txt",
    "open youtube and search funny cats",
    "open calculator" # Single step fallback test
]

print("\n[MASTER BRAIN V7 (Unified) TEST - Legacy V3 Scenarios]")
print("=" * 60)
for cmd in test_commands:
    print(f"USER: {cmd}")
    res = process_command_master_v7(cmd)
    print(f"S1  :\n{res}")
    print("-" * 60)
