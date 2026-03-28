# test_master_brain_v5.py
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from core.master_brain_v7 import process_command_master_v7

print("\n[MASTER BRAIN V7 (Unified) TEST - Legacy V5 Scenarios]")
print("=" * 60)

# CASE 1: Open an app (SAFE) -> Should execute without asking
print("USER: open chrome")
res1 = process_command_master_v7("open chrome")
print(f"S1  : {res1}")

print("\nUSER: no close it")
res2 = process_command_master_v7("no close it")
print(f"S1  : {res2}")
print("-" * 60)

# CASE 2: Create a file (MEDIUM risk) -> Ask permission first time
print("USER: create file secret.txt")
res3 = process_command_master_v7("create file secret.txt")
print(f"S1  : {res3}")

print("\nUSER: yes do it")
res4 = process_command_master_v7("yes do it")
print(f"S1  : {res4}")
print("-" * 60)

# CASE 3: Delete a file (DANGEROUS risk) -> Blocked or Double Confirm
print("USER: delete file secret.txt")
res5 = process_command_master_v7("delete file secret.txt")
print(f"S1  : {res5}")

print("\nUSER: yes delete it")
res6 = process_command_master_v7("yes delete it")
print(f"S1  : {res6}")
print("-" * 60)

# CASE 4: App not found -> Self Healing
print("USER: open fakeapp")
res7 = process_command_master_v7("open fakeapp")
print(f"S1  : {res7}")
print("-" * 60)

# CASE 5: Autonomy Suggestion
print("USER: search python tutorial")
res8 = process_command_master_v7("search python tutorial")
print(f"S1  : {res8}")

print("\nUSER: yes")
res9 = process_command_master_v7("yes")
print(f"S1  : {res9}")
print("-" * 60)
