<p align="center">
  <img src="https://via.placeholder.com/200x200?text=AndroMate" alt="AndroMate Logo" width="200"/>
  
  <h1 align="center">AndroMate</h1>
  
  <p align="center">
    <strong>A powerful, modular AI assistant for Termux on Android.</strong><br>
    <sub>Control your device with natural voice commands, CLI, or automated background tasks.</sub>
  </p>

  <p align="center">
    <a href="https://github.com/Anon4You/AndroMate/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
    </a>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg" alt="Made with Python">
    </a>
    <a href="https://termux.com/">
      <img src="https://img.shields.io/badge/Platform-Termux%20%7C%20Android-green.svg" alt="Platform">
    </a>
    <a href="https://github.com/Anon4You/AndroMate/issues">
      <img src="https://img.shields.io/badge/Status-Beta-orange.svg" alt="Status">
    </a>
  </p>
</p>

---

## 📖 Table of Contents

- [✨ Features](#-features)
- [🎨 Demo](#-demo)
- [📦 Requirements](#-requirements)
- [🚀 Installation](#-installation)
- [💻 Usage](#-usage)
- [⚙️ Configuration](#️-configuration)
- [🧩 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

### 🧠 Core Intelligence
- **Multi-Provider AI:** Seamlessly switch between **OpenRouter**, **OpenAI**, and **Pollinations** (free, no-key required).
- **Voice Recognition:** Hands-free control via Google Speech-to-Text.
- **Conversational Context:** Understands natural queries like "How are you?" or "Who are you?".
- **Spoken Feedback:** Uses `termux-tts-speak` for audible confirmations.

### 📱 Device Control & Automation
- **Communication:** Send SMS, WhatsApp, Telegram, and Email. Auto-resolves contact names.
- **System Management:** Execute shell commands, control brightness, volume, WiFi, and battery monitoring.
- **Media & Hardware:** Take photos, toggle torch, play/pause media, and fetch GPS location.
- **Background Monitoring:**
  - **Clipboard Watcher:** Automatically translates or summarizes copied text.
  - **Notification Auto-Reply:** intelligently responds to incoming notifications.

### 🎨 Advanced Capabilities
- **Image Generation:** Create AI art using `tgpt` (e.g., "Generate a cyberpunk cat").
- **Modular Design:** Easily extend functionality by adding new action modules.

---

## 📦 Requirements

Ensure the following dependencies are installed in your Termux environment.

### System Packages
| Package | Description | Install Command |
| :--- | :--- | :--- |
| **Termux:API App** | Essential bridge for hardware access | [Download from F-Droid](https://f-droid.org/packages/com.termux.api/) |
| `termux-api` | API interface package | `pkg install termux-api` |
| `ffmpeg` | Audio encoding/decoding | `pkg install ffmpeg` |
| `flac` | FLAC audio codec | `pkg install flac` |
| `termux-tts-speak` | Text-to-speech engine | `pkg install termux-tts-speak` |
| `tgpt` | Local AI/Image generation backend | `pkg install tgpt` |

### Python Libraries
```bash
pip install requests SpeechRecognition
```

> ⚠️ **Permission Grant:** After installing the Termux:API app, run commands like `termux-microphone-record` or `termux-sms-send` once manually to grant necessary Android permissions.

---

## 🚀 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Anon4You/AndroMate.git
   cd AndroMate
   ```

2. **Configure API Keys (Optional)**
   Required only for OpenRouter or OpenAI providers. Pollinations works out-of-the-box.
   ```bash
   echo "your-openrouter-api-key" > ~/.openrouter_key
   ```

3. **Run the Assistant**
   ```bash
   python andromate.py voice
   ```

---

## 💻 Usage

AndroMate offers three distinct operational modes:

| Mode | Command | Description |
| :--- | :--- | :--- |
| **Voice** | `python andromate.py voice` | Listens for a single voice command, executes it, and provides feedback. |
| **CLI** | `python andromate.py cli` | Interactive shell mode for typing commands. Great for debugging. |
| **Daemon** | `python andromate.py` | Background mode. Monitors notifications and clipboard changes. |

### 🗣️ Example Commands

**Messaging & Calls**
> "Send a WhatsApp message to John saying I'm on my way."
> "Call Mom."

**System & Utilities**
> "What's my battery level?"
> "Set brightness to 50%."
> "Update system packages." (Executes `pkg update`)

**AI & Media**
> "Generate an image of a futuristic city."
> "Switch to OpenAI provider."
> "What providers are available?"

---

## ⚙️ Configuration

Configuration settings are stored in `~/.andromate/config.json` (auto-generated on first run) or managed via voice commands.

- **Switching Providers:**
  - Voice: *"Switch to pollinations"*
  - Config: Edit the `provider` key in `config.json`.
- **Rate Limiting:** Adjust `MIN_AI_CALL_INTERVAL` in `modules/config.py` to prevent API spamming.
- **Custom App Mapping:** Add specific app aliases to `APP_NAME_TO_PACKAGE` in `modules/config.py`.

---

## 🧩 Project Structure

The project follows a modular architecture for easy maintenance and extension.

```
AndroMate/
├── andromate.py          # Main entry point
└── modules/
    ├── __init__.py
    ├── actions.py        # Core action implementations (Call, SMS, Torch)
    ├── ai.py             # AI decision routing logic
    ├── cli.py            # Interactive CLI loop
    ├── clipboard.py      # Clipboard monitoring service
    ├── config.py         # Static constants and configuration
    ├── contacts.py       # Fuzzy contact name matching
    ├── error_handler.py  # Centralized error logging
    ├── main.py           # Background daemon logic
    ├── notifications.py  # Notification listener
    ├── prompt_manager.py # Dynamic AI prompt generation
    ├── providers.py      # API wrappers (OpenRouter, Pollinations, etc.)
    ├── utils.py          # Helpers (TTS, fuzzy matching, etc.)
    └── voice.py          # Recording & Speech-to-Text logic
```

---

## 🧪 Status & Roadmap

AndroMate is currently in **Active Development (Beta)**.

- [x] Core Voice & CLI functionality
- [x] Multi-provider support
- [ ] GUI Dashboard (Planned)
- [ ] Enhanced Context Awareness

We welcome contributions! Please see `CONTRIBUTING.md` for guidelines.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Developed with ❤️ by <a href="https://github.com/Anon4You">Anon4You</a>
</p>

