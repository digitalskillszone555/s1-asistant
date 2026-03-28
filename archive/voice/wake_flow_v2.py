# voice/wake_flow_v2.py
# S1 Assistant - Wake Flow V2
# Focus: Zero-delay wake detection and command capture.

import speech_recognition as sr
import time
from speech.stt_engine_v2 import get_stt_v2
from utils.state import get_state_manager, AssistantState

class WakeFlowV2:
    """
    Improved wake flow that reduces the gap between wake word and command detection.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.stt_v2 = get_stt_v2()
        self.state_manager = get_state_manager()
        
        # Indian environment tuning (Consistent with WakeWordListener)
        self.recognizer.energy_threshold = 280
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.5
        
        self.wake_words = [
            "s1", "hey s1", "assistant", "hey assistant",
            "hello s1", "hello assistant", "oi s1"
        ]

        self.microphone = None
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[WakeFlowV2] Initialization Complete.")
        except Exception as e:
            print(f"[WakeFlowV2 ERROR] Mic failed: {e}")

    def capture_command(self, lang_code="en-IN"):
        """
        Continuously listens and returns the command text immediately
        if a wake word is detected within the phrase.
        """
        if not self.microphone:
            return None

        with self.microphone as source:
            print("[WakeFlowV2] Listening for wake word + command...")
            try:
                # Capture a phrase that might contain [Wake Word] + [Command]
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                self.state_manager.set_state(AssistantState.THINKING)
                
                # Transcribe the WHOLE phrase (this avoids the 'stop-start' lag)
                raw_text = self.stt_v2.transcribe(audio, lang_code=lang_code)
                
                if not raw_text:
                    self.state_manager.set_state(AssistantState.IDLE)
                    return None

                # Check if phrase starts with or contains wake word
                detected_wake = None
                for w in self.wake_words:
                    if w in raw_text:
                        detected_wake = w
                        break
                
                if detected_wake:
                    print(f"[WakeFlowV2] Wake detected: '{detected_wake}'")
                    # Strip wake word and return command
                    command = raw_text.split(detected_wake, 1)[-1].strip()
                    
                    if not command:
                        print("[WakeFlowV2] No command followed wake word.")
                        # Could return "YES" here but we prefer returning the actual command
                        return "hello" # Dummy command to trigger greeting

                    return command

            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"[WakeFlowV2 ERROR] {e}")
                self.state_manager.set_state(AssistantState.IDLE)

        return None

# Singleton instance
_wake_flow_instance = None

def get_wake_flow_v2():
    global _wake_flow_instance
    if _wake_flow_instance is None:
        _wake_flow_instance = WakeFlowV2()
    return _wake_flow_instance

# Test Function
if __name__ == "__main__":
    flow = get_wake_flow_v2()
    print("Speak: 'Hey S1, open chrome'")
    result = flow.capture_command()
    print(f"FINAL COMMAND: {result}")
