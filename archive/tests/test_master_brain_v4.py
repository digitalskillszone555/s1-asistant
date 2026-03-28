# test_master_brain_v4.py
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from core.master_brain_v7 import process_command_master_v7

print("\n[MASTER BRAIN V7 (Unified) TEST - Legacy V4 Scenarios]")
print("=" * 60)

# CASE 1: Open an app and then decide to close it (No/Negative response)
print("USER: open chrome")
res1 = process_command_master_v7("open chrome")
print(f"S1  : {res1}")

print("\nUSER: no close it")
res2 = process_command_master_v7("no close it")
print(f"S1  : {res2}")
print("-" * 60)

# CASE 2: Multi-tasking then keeping an app open (Yes/Positive response)
print("USER: search cats then open notepad")
res3 = process_command_master_v7("search cats then open notepad")
print(f"S1  : {res3}")

print("\nUSER: yes keep it open")
res4 = process_command_master_v7("yes keep it open")
print(f"S1  : {res4}")
print("-" * 60)
