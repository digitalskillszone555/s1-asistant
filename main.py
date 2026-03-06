import time
import sys
import threading
import argparse
from core.brain import think
from utils.state import get_state_manager, AssistantState
from system.reminder_manager import get_reminder_manager
from system.automation_manager import initialize_automation_manager, get_automation_manager
from system.mode_manager import get_mode_manager
from system.actions import perform_action
from interface_layer.device_detector import detect_device_type
from remote.studio_connector import register_assistant

# --- New Imports for Setup & Config ---
from system.setup_manager import perform_setup_if_needed
from system.config_loader import load_config, set_secure_config_passphrase # Modified import
from config.secure_config import secure_config_exists, secure_config_salt_exists # New import
from voice.voice_input import VoiceInput
from voice.voice_output import VoiceOutput
from voice.wake_word import WakeWordListener
from utils.logging_utils import log_event # Centralized logging

# --- New UI Launcher Import ---
from ui.ui_launcher import launch_interface
from analytics.studio_reporter import send_event

# --- Global Shutdown Event ---
shutdown_event = threading.Event() # Shared event to signal graceful shutdown

def background_checker_thread(shutdown_event: threading.Event):
    """
    This function runs in a separate thread to perform periodic checks and maintenance tasks.
    """
    automation_manager = get_automation_manager()
    while not shutdown_event.is_set(): # Check shutdown event
        try:
            if automation_manager:
                automation_manager.run_workflow("periodic_check")
            shutdown_event.wait(60) # Wait for 60 seconds or until event is set
        except Exception as e:
            log_event("BACKGROUND_CHECKER", f"ERROR: {e}", level="ERROR")
            shutdown_event.wait(60) # Wait even on error to prevent busy-looping

def run_core_logic(config: dict, shutdown_event: threading.Event):
    """
    This function contains the primary loop for the assistant.
    It runs in a background thread and handles voice or text interaction.
    """
    # --- System Initialization ---
    log_event("CORE_LOGIC", "S1 Assistant Core Logic Thread Started.")
    device_type = detect_device_type()
    log_event("CORE_LOGIC", f"Device Type Detected: {device_type.upper()}")

    state_manager = get_state_manager()
    reminder_manager = get_reminder_manager()
    mode_manager = get_mode_manager()

    # --- Conditional Voice Service Initialization ---
    voice_enabled = config.get("voice_enabled", False)
    listener, speaker, wake_word_listener = None, None, None

    if voice_enabled:
        log_event("MAIN", "Voice services enabled.")
        listener = VoiceInput()
        speaker = VoiceOutput()
        wake_word_listener = WakeWordListener()
    else:
        log_event("MAIN", "Voice services disabled. Using text-based interaction.")
        speaker = type('TextSpeaker', (), {'speak': lambda msg: log_event("MAIN", f"Assistant: {msg}")})()

    action_executors = {
        "open": lambda entity: perform_action("open", entity),
        "close": lambda entity: perform_action("close", entity),
        "speak": speaker.speak if speaker else lambda msg: log_event("MAIN", f"Assistant: {msg}"),
    }
    automation_manager = initialize_automation_manager(action_executors)

    checker_thread = threading.Thread(target=background_checker_thread, args=(shutdown_event,), daemon=True)
    checker_thread.start()
    register_assistant()
    if automation_manager:
        automation_manager.run_workflow("on_startup")

    # Main Loop
    SESSION_TIMEOUT = 300 # 5 minutes
    last_interaction_time = time.time()
    
    # Use a dummy listener for text input if voice is disabled
    if not listener:
        listener = type('TextListener', (), {'listen': lambda: input("You: ")})()

    while not shutdown_event.is_set(): # Check shutdown event
        try:
            current_state = state_manager.get_state()

            if current_state in [AssistantState.IDLE, AssistantState.WAITING]:
                if reminder_manager:
                    notification = reminder_manager.get_notification()
                    if notification:
                        mode_settings = mode_manager.get_current_mode_settings()
                        if mode_settings.get("notification_volume") == "speak":
                            speaker.speak(notification)
                        else:
                            log_event("MAIN", f"[SILENT_NOTIFICATION] {notification}")
                        last_interaction_time = time.time()
                        continue
            
            if current_state == AssistantState.IDLE:
                if wake_word_listener and wake_word_listener.listen_for_wake_word():
                    last_interaction_time = time.time()
                    speaker.speak("Yes?")
                elif not wake_word_listener:
                    state_manager.set_state(AssistantState.LISTENING)
                else:
                    shutdown_event.wait(0.1) # Use wait to check event regularly
                continue
            
            if time.time() - last_interaction_time > SESSION_TIMEOUT and voice_enabled:
                state_manager.set_state(AssistantState.IDLE)
                speaker.speak("Going to sleep.")
                continue
            
            if current_state == AssistantState.WAITING:
                shutdown_event.wait(0.5) # Use wait to check event regularly
                state_manager.set_state(AssistantState.LISTENING)
                continue

            if current_state == AssistantState.LISTENING:
                user_text = listener.listen()
                if user_text:
                    last_interaction_time = time.time()
                    reply, _ = think(user_text)
                    speaker.speak(reply)
                    state_manager.set_state(AssistantState.WAITING if voice_enabled else AssistantState.LISTENING)
                elif voice_enabled:
                    state_manager.set_state(AssistantState.IDLE)
            
            shutdown_event.wait(0.1) # Use wait to check event regularly
        except (EOFError, KeyboardInterrupt):
            log_event("CORE_LOGIC", "Shutdown signal received (KeyboardInterrupt).")
            shutdown_event.set() # Set event on manual interrupt
            break
        except Exception as e:
            try:
                send_event("error", str(e))
            except Exception:
                pass # Fail silently
            log_event("CORE_LOGIC", f"ERROR: {e}", level="ERROR")
            state_manager.set_state(AssistantState.IDLE)
            shutdown_event.wait(0.1)

if __name__ == "__main__":
    perform_setup_if_needed()
    
    # --- Secure Config Passphrase Handling ---
    if secure_config_exists() or secure_config_salt_exists():
        passphrase = None
        while not passphrase:
            passphrase = input("Enter passphrase for secure config: ")
            if not passphrase:
                print("Passphrase cannot be empty. Please try again.")
        set_secure_config_passphrase(passphrase)
        log_event("MAIN", "Passphrase for secure config set.")
    else:
        log_event("MAIN", "Secure config or salt not found. Passphrase not requested.", level="WARNING")

    user_config = load_config()
    if not user_config:
        log_event("MAIN", "FATAL: Configuration could not be loaded. Exiting.", level="FATAL")
        print("[Main FATAL] Configuration could not be loaded. Exiting.") # Keep print for immediate visibility
        sys.exit(1)

    parser = argparse.ArgumentParser(description="S1 Assistant")
    parser.add_argument("--ui", action="store_true", help="Launch with the graphical user interface.")
    parser.add_argument("--tray", action="store_true", help="Launch with a system tray icon.")
    parser.add_argument("--api", action="store_true", help="Start the FastAPI server.")
    parser.add_argument("--remote-control", action="store_true", help="Start the local remote control server.")
    parser.add_argument("--test-skills", action="store_true", help="Run the skill test harness and exit.")
    args = parser.parse_args()

    if args.test_skills:
        from skills.test_runner import run_all_skill_tests
        success = run_all_skill_tests()
        log_event("MAIN", "Skill test harness finished.", success=success)
        sys.exit(0 if success else 1)

    log_event("MAIN", "S1 Assistant Starting...")
    
    core_thread = threading.Thread(target=run_core_logic, args=(user_config, shutdown_event,), daemon=True)
    core_thread.start()
    log_event("MAIN", "Core logic thread started.")

    if args.tray:
        launch_interface(ui_type='tray')

    if args.api:
        try:
            from api import server as api_server
            api_server.run_in_thread(shutdown_event=shutdown_event)
            log_event("MAIN", "FastAPI server initiated.")
        except Exception as e:
            log_event("MAIN", f"FastAPI server ERROR: {e}", level="ERROR")
            print(f"[Main API ERROR] {e}")

    if args.remote_control:
        try:
            from remote import control_server
            control_server.run_in_background(shutdown_event=shutdown_event)
            log_event("MAIN", "Remote control server initiated.")
        except Exception as e:
            log_event("MAIN", f"Remote control server ERROR: {e}", level="ERROR")
            print(f"[Main Remote Control ERROR] {e}")

    # --- Main Thread Behavior ---
    if args.ui:
        launch_interface(ui_type='desktop')
    else:
        mode_str = " + ".join(filter(None, ["Headless", "Tray" if args.tray else None, "API" if args.api else None, "Remote Control" if args.remote_control else None]))
        log_event("MAIN", f"Running in {mode_str} mode. Press Ctrl+C to exit.")
        try:
            while not shutdown_event.is_set():
                shutdown_event.wait(1)
            
            log_event("MAIN", "Shutdown event received. Waiting for core logic to finish...")
            core_thread.join(timeout=5)
            if core_thread.is_alive():
                log_event("MAIN", "Core logic thread did not terminate gracefully.", level="WARNING")

        except KeyboardInterrupt:
            log_event("MAIN", "KeyboardInterrupt received in main thread.")
            shutdown_event.set()
            log_event("MAIN", "Shutdown signal sent to background threads.")
            core_thread.join(timeout=5)
            if core_thread.is_alive():
                log_event("MAIN", "Core logic thread did not terminate gracefully.", level="WARNING")

    log_event("MAIN", "S1 Assistant Stopped.")