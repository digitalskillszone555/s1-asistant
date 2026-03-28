# test_master_brain_v6.py
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from core.master_brain_v7 import process_command_master_v7

print("\n[MASTER BRAIN V7 (Unified) TEST - Legacy V6 Scenarios]")
print("=" * 60)

# CASE 1: Open and then close with context "it"
print("USER: open chrome")
res1 = process_command_master_v7("open chrome")
print(f"S1  : {res1}")

print("\nUSER: close it")
res2 = process_command_master_v7("close it")
print(f"S1  : {res2}")
print("-" * 60)

# CASE 2: Native Bengali command
print("USER: open notepad")
res3 = process_command_master_v7("open notepad")
print(f"S1  : {res3}")

print("\nUSER: বন্ধ করো")
res4 = process_command_master_v7("বন্ধ করো")
print(f"S1  : {res4}")
print("-" * 60)

# CASE 3: Banglish command with specific name
print("USER: browser kete dao")
res5 = process_command_master_v7("browser kete dao")
print(f"S1  : {res5}")
print("-" * 60)
