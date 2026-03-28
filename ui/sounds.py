# ui/sounds.py
import winsound
import threading

def play_sound(sound_type):
    """Plays a system sound or placeholder based on sound_type."""
    def run():
        try:
            if sound_type == "LISTENING":
                # A short high beep
                winsound.Beep(1000, 150)
            elif sound_type == "DONE":
                # Two short beeps (success)
                winsound.Beep(800, 100)
                winsound.Beep(1200, 100)
            elif sound_type == "ERROR":
                # Low beep
                winsound.Beep(400, 400)
        except Exception as e:
            print(f"[Sound Error] {e}")

    threading.Thread(target=run, daemon=True).start()
