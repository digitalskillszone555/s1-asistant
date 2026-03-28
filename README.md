# S1 Assistant - Global Edition

S1 is a powerful, production-ready virtual assistant with a premium human-like interface. It supports voice-first interactions, multi-step tasks, and emotional intelligence.

## Features
- **Modern Animated UI:** Siri-like orb with emotional reactions.
- **Voice-First:** Background wake word ("Hey S1") and interruptible speech.
- **Unified Brain (V7):** Context-aware, proactive, and secure.
- **Smart Memory:** Learns your name, preferences, and habits.
- **Secure by Design:** Hardened action guard prevents dangerous commands.
- **Multi-lingual:** Supports English, Bengali, and Hindi.

## How to Run
1. Install dependencies:
   ```bash
   pip install customtkinter speechrecognition pyttsx3 google-generativeai requests cryptography
   ```
2. Start the assistant:
   ```bash
   python main.py --premium
   ```

## Folder Structure
- `core/`: Central nervous system (Brain, Action Engine).
- `nlp/`: Language processing and emotion detection.
- `ui/`: Premium and legacy user interfaces.
- `voice/`: Wake word and speech modules.
- `memory/`: Encrypted persistent storage.
- `security/`: Command filtering and safety.
- `config/`: System and AI configuration.
- `archive/`: Legacy versions and unused files.

## Documentation
- [Architecture](ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)
