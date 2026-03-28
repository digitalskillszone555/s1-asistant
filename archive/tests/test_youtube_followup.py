# test_youtube_followup.py
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from core.master_brain_v7 import process_command_master_v7

print("\n[YOUTUBE FOLLOW-UP TEST]")
print("=" * 60)

# 1. Open YouTube
print("USER: open youtube")
res1 = process_command_master_v7("open youtube")
print(f"S1  : {res1}")

# 2. Contextual search (Should now use YouTube search because last app was youtube)
print("\nUSER: search for funny cats")
res2 = process_command_master_v7("search for funny cats")
print(f"S1  : {res2}")
print("-" * 60)
