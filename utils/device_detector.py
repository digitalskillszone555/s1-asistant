# utils/device_detector.py

import platform
import os

def detect_device_type():
    """
    Detects the type of device the assistant is running on.
    For now, it primarily detects desktop OS and has placeholders for web/mobile.
    """
    system = platform.system()
    
    # Check for web environment (e.g., Pyodide in a browser)
    if 'PYODIDE_URL' in os.environ:
        return "web"
        
    # Check for mobile environment (e.g., Kivy on Android/iOS)
    # This is a placeholder; a real implementation would be more robust.
    if 'KIVY_PLATFORM' in os.environ:
        return "mobile"

    # Default to desktop for standard operating systems
    if system in ["Windows", "Linux", "Darwin"]:
        return "desktop"
        
    return "unknown"
