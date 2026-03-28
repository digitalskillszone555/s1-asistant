# ui/ui_launcher.py
# S1 Assistant - UI Launcher
# Focus: Routing to the premium desktop interface or system tray.

from interface_layer.device_detector import detect_device_type

def get_platform():
    """Detects the current platform (e.g., 'desktop')."""
    return detect_device_type()

def launch_desktop_ui():
    """
    Launches the premium desktop window.
    """
    try:
        from ui.premium_app import PremiumS1App
        print("[UI Launcher] Launching S1 Premium Interface...")
        app = PremiumS1App()
        app.mainloop()
    except ImportError as e:
        print(f"[UI Launcher ERROR] CustomTkinter not found. Please install it to use the premium UI.")
    except Exception as e:
        print(f"[UI Launcher ERROR] Failed to launch UI: {e}")

def launch_tray_mode():
    """
    Launches the system tray icon.
    """
    try:
        from ui.tray_manager import TrayManager
        print("[UI Launcher] Initiating System Tray mode...")
        # Tray icon can launch the premium UI
        tray_manager = TrayManager(ui_launcher=launch_desktop_ui)
        tray_manager.run_in_thread()
    except Exception as e:
        print(f"[UI Launcher TRAY ERROR] {e}")

def launch_interface(ui_type: str):
    """
    Acts as a UI router.
    """
    platform = get_platform()
    print(f"[UI Launcher] Platform: {platform} | Requested: {ui_type}")

    if platform == "desktop":
        if ui_type in ['desktop', 'premium']:
            launch_desktop_ui()
        elif ui_type == 'tray':
            launch_tray_mode()
    else:
        print(f"[UI Launcher] UI not yet implemented for platform: {platform}")
