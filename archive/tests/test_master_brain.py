# test_master_brain.py
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from core.master_brain_v7 import process_command_master_v7

test_commands = [
    "open chrome",
    "search kittens",
    "youtube funny cats",
    "create file s1_test.txt",
    "write hello from s1 in s1_test.txt",
    "open file s1_test.txt"
]

print("\n[MASTER BRAIN V7 (Unified) TEST - Legacy V2 Scenarios]")
print("=" * 50)
for cmd in test_commands:
    print(f"USER: {cmd}")
    res = process_command_master_v7(cmd)
    print(f"S1  : {res}")
    print("-" * 50)
