# =========================
# S1 ASSISTANT VOICE OUTPUT
# Phase 3: Interruptible Engine
# =========================

import pyttsx3
import threading
from utils.state import get_state_manager, AssistantState
from analytics.studio_reporter import send_event

class VoiceOutput:
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self._lock = threading.Lock()

    def _init_engine(self):
        with self._lock:
            if self.engine is None:
                self.engine = pyttsx3.init()
                # Optional: Configure voice properties here
                # self.engine.setProperty('rate', 175)

    def speak(self, text: str):
        """
        Uses pyttsx3 to speak the given text.
        Allows interruption via stop() method.
        """
        if not text:
            return
            
        self._init_engine()
        state_manager = get_state_manager()
        state_manager.set_state(AssistantState.SPEAKING)
        
        try:
            send_event("speaking", "Speaking response")
        except Exception:
            pass
        
        self.is_speaking = True
        print(f"S1: {text}")
        
        try:
            # We use a loop or chunks if we want even finer control,
            # but for now, engine.say + engine.runAndWait is the standard.
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[TTS ERROR] {e}")
        finally:
            self.is_speaking = False
            # Transition to WAITING for a few seconds to allow follow-up
            state_manager.set_state(AssistantState.WAITING)

    def stop(self):
        """Interrupts the current speech immediately."""
        if self.is_speaking and self.engine:
            print("[TTS] Interrupted by user.")
            try:
                self.engine.stop()
                self.is_speaking = False
            except Exception as e:
                print(f"[TTS STOP ERROR] {e}")

# Global instance for easier access during interrupts
S1_SPEAKER = VoiceOutput()

def get_voice_output():
    return S1_SPEAKER
