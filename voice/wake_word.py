# voice/wake_word.py
import speech_recognition as sr
import time
import threading
from utils.state import get_state_manager, AssistantState

class WakeWordListener:
    """
    Continuous background listener for the wake word "Hey S1".
    Optimized for low CPU usage and non-blocking operation.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Energy threshold tuning for background listening
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        
        self.microphone = None
        self.state_manager = get_state_manager()
        self.stop_listening = None
        
        # Wake Words (including common misinterpretations)
        self.wake_words = [
            "hey s1", "s1", "hi s1", "hello s1", 
            "hay s1", "he s1", "hey s 1", "s 1"
        ]
        
        self.last_detection_time = 0
        self.cooldown = 2.0  # seconds

        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[WAKE] Wake word engine initialized.")
        except Exception as e:
            print(f"[WAKE ERROR] Microphone not available: {e}")
            self.microphone = None

    def _callback(self, recognizer, audio):
        """
        Callback function for background listening.
        Triggered whenever speech is detected.
        """
        # Only process if we are IDLE or WAITING
        current_state = self.state_manager.get_state()
        if current_state not in [AssistantState.IDLE, AssistantState.WAITING]:
            return

        # Cooldown check
        if time.time() - self.last_detection_time < self.cooldown:
            return

        try:
            # Use Google STT for wake word detection (lightweight for short phrases)
            # Offline would be better but requires models.
            text = recognizer.recognize_google(audio, language="en-IN").lower()
            print(f"[WAKE HEARD] {text}")

            if any(w in text for w in self.wake_words):
                print(f"[WAKE DETECTED] Triggering S1...")
                self.last_detection_time = time.time()
                
                # Update state to trigger main loop
                self.state_manager.set_state(AssistantState.LISTENING)
                
                # If there's a UI, it should react to this state change
                # (handled by individual UI polling logic)
                
        except sr.UnknownValueError:
            pass # Speech was not intelligible
        except Exception as e:
            print(f"[WAKE CALLBACK ERROR] {e}")

    def start(self):
        """Starts the background listening thread."""
        if not self.microphone:
            print("[WAKE] Cannot start: No microphone found.")
            return False
            
        if self.stop_listening:
            print("[WAKE] Already running.")
            return True

        print("[WAKE] Starting background listener...")
        self.stop_listening = self.recognizer.listen_in_background(self.microphone, self._callback)
        return True

    def stop(self):
        """Stops the background listening thread."""
        if self.stop_listening:
            print("[WAKE] Stopping background listener...")
            self.stop_listening(wait_for_stop=False)
            self.stop_listening = None

    def listen_for_wake_word(self):
        """
        Legacy compatibility method for the main loop.
        Returns True if the state was recently changed to LISTENING.
        """
        return self.state_manager.is_state(AssistantState.LISTENING)

if __name__ == "__main__":
    # Test script
    listener = WakeWordListener()
    listener.start()
    print("Wake word listener active. Say 'Hey S1'...")
    try:
        while True:
            time.sleep(1)
            if get_state_manager().is_state(AssistantState.LISTENING):
                print(">>> MAIN LOOP: WAKE WORD DETECTED! <<<")
                get_state_manager().set_state(AssistantState.IDLE) # Reset for testing
    except KeyboardInterrupt:
        listener.stop()
