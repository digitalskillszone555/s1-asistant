import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.master_brain_v7 import process_command_master_v7

def route_command(text):
    reply = process_command_master_v7(text)
    exit_flag = False # Standardize on no exit flag from brain itself
    return reply, exit_flag
