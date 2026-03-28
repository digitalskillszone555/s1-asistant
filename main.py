import time
import sys
import threading
import argparse
from core.master_brain_v7 import process_command_master_v7
from utils.state import get_state_manager, AssistantState
from system.reminder_manager import get_reminder_manager
from system.automation_manager import initialize_automation_manager, get_automation_manager
from system.mode_manager import get_mode_manager
from core.action_engine import get_action_engine
from interface_layer.device_detector import detect_device_type
from remote.studio_connector import register_assistant
from system.setup_manager import perform_setup_if_needed
from system.config_loader import load_config, set_secure_config_passphrase
from system.health_check import run_health_check # New
from config.secure_config import secure_config_exists, secure_config_salt_exists
from voice.voice_input import VoiceInput
from voice.voice_output import get_voice_output
from voice.wake_word import WakeWordListener
from utils.logging_utils import log_event
from ui.ui_launcher import launch_interface
from analytics.studio_reporter import send_event

shutdown_event = threading.Event()

def background_checker_thread(shutdown_event: threading.Event):
    automation_manager = get_automation_manager()
    while not shutdown_event.is_set():
        try:
            if automation_manager:
                automation_manager.run_workflow("periodic_check")
            shutdown_event.wait(60)
        except Exception as e:
            log_event("BACKGROUND_CHECKER", f"ERROR: {e}", level="ERROR")
            shutdown_event.wait(60)

def run_core_logic(config: dict, shutdown_event: threading.Event):
    log_event("CORE_LOGIC", "S1 Assistant Core Logic Thread Started.")
    
    # --- System Health Check ---
    health_success, health_report = run_health_check(config)
    if not health_success:
        print(f"[WARN] Some modules failed health check: {health_report}")
    
    state_manager = get_state_manager()
    reminder_manager = get_reminder_manager()
    mode_manager = get_mode_manager()

    voice_enabled = config.get("voice_enabled", False)
    listener, speaker, wake_word_listener = None, None, None

    if voice_enabled:
        log_event("MAIN", "Voice services enabled.")
        listener = VoiceInput()
        speaker = get_voice_output()
        wake_word_listener = WakeWordListener()
        wake_word_listener.start()
    else:
        log_event("MAIN", "Voice services disabled.")
        speaker = type('TextSpeaker', (), {
            'speak': lambda msg: log_event("MAIN", f"Assistant: {msg}"),
            'stop': lambda: None
        })()

    action_engine = get_action_engine()
    action_executors = {
        "open": lambda entity: action_engine.execute({"intent": "open_app", "entity": entity}),
        "close": lambda entity: action_engine.execute({"intent": "close_app", "entity": entity}),
        "speak": speaker.speak,
    }
    automation_manager = initialize_automation_manager(action_executors)

    checker_thread = threading.Thread(target=background_checker_thread, args=(shutdown_event,), daemon=True)
    checker_thread.start()
    register_assistant()
    if automation_manager:
        automation_manager.run_workflow("on_startup")

    # Main Loop
    SESSION_TIMEOUT = 300
    WAIT_FOR_FOLLOWUP = 7
    
    if not listener:
        listener = type('TextListener', (), {'listen': lambda: input("You: ")})()

    while not shutdown_event.is_set():
        try:
            current_state = state_manager.get_state()

            if current_state in [AssistantState.IDLE, AssistantState.WAITING]:
                if reminder_manager:
                    notification = reminder_manager.get_notification()
                    if notification:
                        speaker.speak(notification)
                        continue
            
            if current_state == AssistantState.IDLE:
                if not wake_word_listener:
                    state_manager.set_state(AssistantState.LISTENING)
                else:
                    shutdown_event.wait(0.2)
                continue
            
            if current_state == AssistantState.WAITING:
                if time.time() - state_manager.last_state_change > WAIT_FOR_FOLLOWUP:
                    state_manager.set_state(AssistantState.IDLE)
                    continue
                state_manager.set_state(AssistantState.LISTENING)
                continue

            if current_state == AssistantState.LISTENING:
                user_text = listener.listen()
                if user_text:
                    if any(w in user_text for w in ["stop", "cancel", "wait"]):
                        speaker.stop()
                        state_manager.set_state(AssistantState.IDLE)
                        continue

                    reply = process_command_master_v7(user_text)
                    speaker.speak(reply)
                    state_manager.set_state(AssistantState.WAITING)
                else:
                    if voice_enabled:
                        state_manager.set_state(AssistantState.IDLE)
            
            shutdown_event.wait(0.1)
        except (EOFError, KeyboardInterrupt):
            shutdown_event.set()
            break
        except Exception as e:
            log_event("CORE_LOGIC", f"ERROR: {e}", level="ERROR")
            state_manager.set_state(AssistantState.IDLE)
            shutdown_event.wait(0.1)

if __name__ == "__main__":
    perform_setup_if_needed()
    
    if secure_config_exists() or secure_config_salt_exists():
        passphrase = None
        while not passphrase:
            passphrase = input("Enter passphrase for secure config: ")
            if not passphrase: print("Passphrase cannot be empty.")
        set_secure_config_passphrase(passphrase)

    user_config = load_config()
    if not user_config: sys.exit(1)

    parser = argparse.ArgumentParser(description="S1 Assistant - Production Ready")
    parser.add_argument("--ui", action="store_true")
    parser.add_argument("--premium", action="store_true")
    parser.add_argument("--tray", action="store_true")
    parser.add_argument("--api", action="store_true")
    parser.add_argument("--remote-control", action="store_true")
    parser.add_argument("--test-skills", action="store_true")
    args = parser.parse_args()

    if args.test_skills:
        from root.tests.test_runner import run_all_skill_tests
        sys.exit(0 if run_all_skill_tests() else 1)

    log_event("STARTUP", "S1 Assistant Initializing...")
    
    core_thread = threading.Thread(target=run_core_logic, args=(user_config, shutdown_event,), daemon=True)
    core_thread.start()

    if args.tray: launch_interface(ui_type='tray')
    if args.api:
        from api import server as api_server
        api_server.run_in_thread(shutdown_event=shutdown_event)
    if args.remote_control:
        from remote import control_server
        control_server.run_in_background(shutdown_event=shutdown_event)

    if args.premium or args.ui:
        launch_interface(ui_type='premium')

    else:
        try:
            while not shutdown_event.is_set(): shutdown_event.wait(1)
        except KeyboardInterrupt: shutdown_event.set()

    log_event("SHUTDOWN", "S1 Assistant Stopped.")
