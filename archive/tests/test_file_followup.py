# test_file_followup.py
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from core.master_brain_v7 import process_command_master_v7

print("\n[FILE FOLLOW-UP TEST]")
print("=" * 60)

# 1. Create a file
print("USER: create file context_test.txt")
res1 = process_command_master_v7("create file context_test.txt")
print(f"S1  : {res1}")

# 1b. Approve permission
print("\nUSER: yes")
res1b = process_command_master_v7("yes")
print(f"S1  : {res1b}")

# 2. Write to it (Natural command)
print("\nUSER: write testing context system")
res2 = process_command_master_v7("write testing context system")
print(f"S1  : {res2}")

# 2b. Approve write permission
print("\nUSER: yes")
res2b = process_command_master_v7("yes")
print(f"S1  : {res2b}")
print("-" * 60)
