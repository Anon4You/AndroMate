<p align="center">
  <img src="img/img.png" alt="AndroMate Logo" width="200"/>
  
  <h1 align="center">AndroMate</h1>
  
  <p align="center">
    <strong>A powerful, modular AI assistant for Termux on Android.</strong><br>
    <sub>Control your device with natural voice commands, CLI, Web Dashboard, Telegram, or automated background tasks.</sub>
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
- [🌐 Web Dashboard](#-web-dashboard)
- [📱 Remote Control via Telegram](#-remote-control-via-telegram)
- [🔊 Wake Word Activation](#-wake-word-activation)
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
- **Connectivity:** Turn WiFi on via voice command.
- **Media & Hardware:** 
  - **Selfie Mode:** "Take a selfie" automatically uses the front camera.
  - **Smart Torch:** "Front torch" warns about hardware limitations and toggles main flash.
- **Interactive UI:** Uses `termux-toast` for popups and `termux-dialog` for interactive prompts.
- **Background Monitoring:**
  - **Clipboard Watcher:** Automatically translates or summarizes copied text.

### 🌐 Remote Control & Interfaces
- **Web Dashboard:** Monitor and control AndroMate via a local web interface (`http://127.0.0.1:5000`).
- **Telegram Bot:** Control your device from anywhere in the world via a Telegram bot.
- **Enhanced CLI:** Colored output for better readability and persistent command history saved in `~/.andromate/`.

### 🔊 Wake Word Activation
- **True Hands‑Free:** Say a wake word like *"Hey AndroMate"* to activate voice recognition.
- **Continuous Background Listening:** The assistant listens in the background (using `speech_recognition`) and only responds after hearing the wake word.
- **Fuzzy Matching:** Tolerates slight mispronunciations (e.g., "Hey Android" will also trigger).
- **Echo Prevention:** Automatically ignores its own speech, so it never wakes itself up.

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
| `tgpt` | Local AI/Image generation backend | `pkg install tgpt` |
| `tmux` | Terminal multiplexer for background sessions | `pkg install tmux` |
| `flac` | Required for `speech_recognition` (wake word) | `pkg install flac` |

> [!NOTE]
> `ffmpeg` is no longer required as the voice system now uses native Termux speech recognition.

### Python Libraries
```bash
pip install requests SpeechRecognition colorama flask telebot
```

> [!WARNING]
> After installing the Termux:API app, run commands like `termux-speech-to-text` or `termux-sms-send` once manually to grant necessary Android permissions.

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

AndroMate offers multiple operational modes:

| Mode | Command | Description |
| :--- | :--- | :--- |
| **Voice** | `python andromate.py voice` | Listens using native `termux-speech-to-text`, executes commands instantly. |
| **Wake Word** | `python andromate.py wake` | Continuously listens for wake word; when detected, captures and executes voice commands. |
| **CLI** | `python andromate.py cli` | Interactive shell with colored output and saved history. |
| **Web** | `python andromate.py web` | Launches the Flask Web Dashboard. |
| **Telegram** | `python andromate.py telegram` | Starts the Telegram bot for remote control. |
| **Daemon** | `python andromate.py` | Background mode. Monitors clipboard changes. |

### 🗣️ Example Commands

**Messaging & Calls**
> "Send an email to John saying I'll be late."
> "Show all contacts."

**System & Utilities**
> "Turn on WiFi."
> "Take a selfie."

**AI & Media**
> "Generate an image of a futuristic city."
> "Switch to OpenAI provider." (Takes effect immediately)

---

## 🌐 Web Dashboard

Launch the local web server to control AndroMate from your browser:

```bash
python andromate.py web
```

- **Local URL:** `http://127.0.0.1:5000`
- **Security:** Accessible only from the device itself by default.

---

## 📱 Remote Control via Telegram

Control your Android device from anywhere using a Telegram bot.

1. Create a bot with [@BotFather](https://t.me/botfather) and get a token.
2. Add to `~/.andromate/config.json`:
   ```json
   {
     "TELEGRAM_BOT_TOKEN": "your-bot-token",
     "TELEGRAM_AUTHORIZED_CHAT_ID": 123456789
   }
   ```
3. Run: `python andromate.py telegram`

Now any command you send to the bot will be executed on your device (only your chat ID is allowed).

> [!TIP]
> The bot will stop if you close the Termux session. To keep it running in the background, use `tmux`:
> ```bash
> tmux new -s andromate
> python andromate.py telegram
> # Detach with Ctrl+B, then press D
> # Reattach later: tmux attach -t andromate
> ```

---

## 🔊 Wake Word Activation

To run the wake word detector continuously in the background:

```bash
python andromate.py wake
```

The assistant will start listening for your wake word (default: "Hey AndroMate", "Hey Android", etc.). Once detected, it will beep (say "Yes?") and listen for your command. It then processes the command and returns to listening mode.

> [!TIP]
> Use `tmux` to run the wake word listener in the background:
> ```bash
> tmux new -s andromate-wake
> python andromate.py wake
> # Detach with Ctrl+B, D
> ```

### 🛠️ Customizing Wake Words

Edit the `WAKE_WORDS` list in `modules/wake_word.py` to add or change phrases. The system uses fuzzy matching, so slight mispronunciations are still recognised.

> [!NOTE]
> The detector pauses while the assistant is speaking, so it never reacts to its own voice (Echo Prevention).

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

> [!CAUTION]
> Never use your regular Google password.
> 1. Enable 2FA on your Google account.
> 2. Generate an **App Password** specifically for AndroMate.
> 3. Use that 16-character password in the config.

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
    ├── shared.py         # Thread‑safe flags (e.g., speaking state)
    ├── telegram_bot.py   # Telegram bot interface
    ├── utils.py          # Helpers (TTS, fuzzy matching, etc.)
    ├── voice.py          # Native termux-speech-to-text logic
    ├── wake_word.py      # Continuous wake word detector
    └── web_dashboard.py  # Flask web interface backend
```

---

## 🧪 Status & Roadmap

AndroMate is currently in **Active Development (Beta)**.

- [x] Core Voice & CLI functionality
- [x] Native Speech-to-Text integration
- [x] Multi-provider support (Hot-swap)
- [x] Telegram Remote Control
- [x] Web Dashboard
- [x] Wake Word Activation
- [x] Enhanced Context Awareness

We welcome contributions! Please see `CONTRIBUTING.md` for guidelines.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Developed with ❤️ by <a href="https://github.com/Anon4You">Anon4You</a>
</p>
