<p align="center">
  <img src="img/img.png" alt="AndroMate Logo" width="200"/>
  
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
- [📦 Requirements](#-requirements)
- [🚀 Installation](#-installation)
- [💻 Usage](#-usage)
- [⚙️ Configuration](#️-configuration)
- [🧩 Project Structure](#-project-structure)
- [🤝 Contributing](CONTRIBUTING.md)
- [📄 License](#-license)

---

## ✨ Features

### 🧠 Core Intelligence
- **Multi-Provider AI:** Seamlessly switch between **OpenRouter**, **OpenAI**, and **Pollinations** (free, no-key required).
- **Native Voice Recognition:** Hands-free control via `termux-speech-to-text`. Faster, simpler, and works offline.
- **Hot-Swappable Providers:** Switch AI providers instantly via command—no restart required.
- **Spoken Feedback:** Uses `termux-tts-speak` for audible confirmations.

### 📱 Device Control & Automation
- **Communication:**
  - **SMS & Calls:** Send SMS, view call logs with contact names, and make calls.
  - **Email:** Send real background emails via SMTP (Gmail supported).
  - **Messaging Apps:** WhatsApp and Telegram support (opens app with pre-filled message).
- **Enhanced Logs:** Call logs and SMS inbox display contact names, sent/received labels, and message previews.
- **Contact Management:** List all contacts with "show all" support.
- **System Management:** Execute shell commands, control brightness, volume, and monitor battery.
- **Connectivity:** Turn WiFi on via voice command (Note: Termux API does not support disabling WiFi).
- **Media & Hardware:** 
  - **Selfie Mode:** "Take a selfie" automatically uses the front camera.
  - **Smart Torch:** "Front torch" warns about hardware limitations and toggles main flash.
- **Interactive UI:** Uses `termux-toast` for popups and `termux-dialog` for interactive prompts.
- **Background Monitoring:**
  - **Clipboard Watcher:** Automatically translates or summarizes copied text.

### 🎨 Advanced Capabilities
- **Enhanced CLI:** Colored output for better readability and persistent command history saved in `~/.andromate/`.
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
| `tgpt` | Local AI/Image generation backend | `pkg install tgpt` |


### Python Libraries
```bash
pip install requests SpeechRecognition colorama
```

> ⚠️ **Permission Grant:** After installing the Termux:API app, run commands like `termux-speech-to-text` or `termux-sms-send` once manually to grant necessary Android permissions.

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
| **Voice** | `python andromate.py voice` | Listens using native `termux-speech-to-text`, executes commands instantly. |
| **CLI** | `python andromate.py cli` | Interactive shell with colored output and saved history. Great for debugging. |
| **Daemon** | `python andromate.py` | Background mode. Monitors clipboard changes. |

### 🗣️ Example Commands

**Messaging & Calls**
> "Send an email to John saying I'll be late."
> "Show all contacts."
> "Read my last SMS."

**System & Utilities**
> "Turn on WiFi."
> "Take a selfie."

**AI & Media**
> "Generate an image of a futuristic city."
> "Switch to OpenAI provider." (Takes effect immediately)

---

## ⚙️ Configuration

Configuration settings are stored in `~/.andromate/config.json` (auto-generated on first run) or managed via voice commands.

### 📧 Email Setup (SMTP)
To send emails, add your Gmail credentials to `~/.andromate/config.json`:

```json
{
  "EMAIL_SENDER": "your.email@gmail.com",
  "EMAIL_APP_PASSWORD": "your-16-char-app-password"
}
```

1. Enable 2FA on your Google account.
2. Generate an **App Password** (use this instead of your regular password).
3. The assistant will use this to send emails silently in the background.

### General Settings
- **Switching Providers:**
  - Voice: *"Switch to pollinations"* (Changes apply instantly).
  - Config: Edit the `provider` key in `config.json`.
- **CLI History:** Your command history is automatically saved in `~/.andromate/`.

---

## 🧩 Project Structure

The project follows a modular architecture for easy maintenance and extension.

```
AndroMate/
├── andromate.py          # Main entry point
└── modules/
    ├── __init__.py
    ├── actions.py        # Core action implementations (Call, SMS, Email, Selfie)
    ├── ai.py             # AI decision routing logic
    ├── cli.py            # Interactive CLI loop with history
    ├── clipboard.py      # Clipboard monitoring service
    ├── config.py         # Static constants and configuration
    ├── contacts.py       # Fuzzy contact name matching & listing
    ├── error_handler.py  # Centralized error logging
    ├── main.py           # Background daemon logic
    ├── notifications.py  # Toast and Dialog handlers
    ├── prompt_manager.py # Dynamic AI prompt generation
    ├── providers.py      # API wrappers (OpenRouter, Pollinations, etc.)
    ├── utils.py          # Helpers (TTS, fuzzy matching, etc.)
    └── voice.py          # Native termux-speech-to-text logic
```

---

## 🧪 Status & Roadmap

AndroMate is currently in **Active Development (Beta)**.

- [x] Core Voice & CLI functionality
- [x] Native Speech-to-Text integration
- [x] Multi-provider support (Hot-swap)
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
