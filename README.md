# S1 Assistant - Global Edition

S1 is a powerful, production-ready virtual assistant. It supports voice-first interactions, multi-step tasks, and emotional intelligence via terminal or API.

## Features
- **Terminal Mode:** Clean CLI interface for developer focus.
- **Voice-First:** Background wake word ("Hey S1") and interruptible speech.
- **Unified Brain (V7):** Context-aware, proactive, and secure.
- **Smart Memory:** Learns your name, preferences, and habits.
- **Secure by Design:** Hardened action guard prevents dangerous commands.
- **Multi-lingual:** Supports English, Bengali, and Hindi.
- **API Ready:** Integrate S1 into other applications.

## How to Run
1. Install dependencies:
   ```bash
   pip install speechrecognition pyttsx3 google-generativeai requests cryptography fastapi uvicorn
   ```
2. Start the assistant (Terminal Mode):
   ```bash
   python main.py
   ```
3. Start the API server:
   ```bash
   python main.py --api
   ```

## Folder Structure
- `core/`: Central nervous system (Brain, Action Engine).
- `nlp/`: Language processing and emotion detection.
- `voice/`: Wake word and speech modules.
- `memory/`: Encrypted persistent storage.
- `security/`: Command filtering and safety.
- `config/`: System and AI configuration.
- `archive/`: Legacy versions and unused files.

## Documentation
- [Architecture](ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)
