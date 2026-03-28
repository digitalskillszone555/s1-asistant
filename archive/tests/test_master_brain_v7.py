# test_master_brain_v7.py
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from core.master_brain_v7 import process_command_master_v7

print("\n[MASTER BRAIN V7 CONVERSATION TEST]")
print("=" * 60)

# 1. First turn: Open App (Testing Personality & Memory Init)
print("USER: open chrome")
res1 = process_command_master_v7("open chrome")
print(f"S1  : {res1}")

# 2. Second turn: Contextual search (Testing Memory & Intent persistence)
print("\nUSER: search for funny cats")
res2 = process_command_master_v7("search for funny cats")
print(f"S1  : {res2}")

# 3. Third turn: Open something else (Testing Personality variation)
print("\nUSER: search funny videos")
res3 = process_command_master_v7("search funny videos")
print(f"S1  : {res3}")
print("-" * 60)
