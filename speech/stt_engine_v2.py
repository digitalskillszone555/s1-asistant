# speech/stt_engine_v2.py
# S1 Assistant - STT Engine V2
# Focus: Hybrid STT (Offline first) with improved noise handling.

import speech_recognition as sr
from speech.offline_stt import get_offline_stt
import os

class STTEngineV2:
    """
    Improved STT Engine that handles background noise and supports 
    hybrid offline/online recognition.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.offline = get_offline_stt()
        
        # Optimized thresholds for faster response and better noise immunity
        self.recognizer.energy_threshold = 400 
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.6  # Don't wait too long after user stops speaking
        self.recognizer.phrase_threshold = 0.3 # Detect short commands quickly
        self.recognizer.non_speaking_duration = 0.4

    def transcribe(self, audio_data, lang_code="en-IN"):
        """
        Transcribes audio data to text using a hybrid approach.
        """
        if not audio_data:
            return None

        # 1. Try Offline STT (Lowest Latency)
        if self.offline.is_ready:
            # Vosk expects 'en', 'bn', etc.
            simple_lang = lang_code.split("-")[0]
            try:
                text = self.offline.recognize_speech(audio_data, simple_lang)
                if text and len(text.strip()) > 0:
                    print(f"[STT V2] Offline Match: '{text}'")
                    return text.lower()
            except Exception as e:
                print(f"[STT V2 WARN] Offline transcription failed: {e}")

        # 2. Online Fallback (Higher Accuracy for complex sentences)
        try:
            text = self.recognizer.recognize_google(audio_data, language=lang_code)
            if text:
                print(f"[STT V2] Online Match: '{text}'")
                return text.lower()
        except sr.UnknownValueError:
            pass # No speech detected
        except sr.RequestError as e:
            print(f"[STT V2 ERROR] Online service error: {e}")
        except Exception as e:
            print(f"[STT V2 ERROR] Unexpected: {e}")

        return None

# Singleton instance
_stt_v2_instance = None

def get_stt_v2():
    global _stt_v2_instance
    if _stt_v2_instance is None:
        _stt_v2_instance = STTEngineV2()
    return _stt_v2_instance
