```markdown
<p align="center">
  <img src="img/img.png" alt="AndroMate Logo" width="200"/>

  <h1 align="center">AndroMate</h1>

  <p align="center">
    <strong>A powerful, modular AI assistant for Termux on Android.</strong><br>
    <sub>Control your device with voice, CLI, Web Dashboard, Telegram, or automated background tasks.</sub>
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

## Features

### Core Intelligence
- **Multi-Provider AI:** Switch between **OpenRouter**, **OpenAI**, and **Pollinations** (free, no key required) — hot-swap without restart.
- **Coding Agent:** Read, write, execute, and debug code in an automated loop until the task resolves.
- **Native Voice Recognition:** Hands-free control via `termux-speech-to-text` — no ffmpeg, works offline.
- **Wake Word Activation:** Continuous background listening with fuzzy matching and echo prevention.
- **Spoken Feedback:** Audible confirmations via `termux-tts-speak`.
- **Image Generation:** Create AI art using `tgpt` (e.g., "Generate a cyberpunk cat").

### Device Control
- **SMS & Calls:** Send messages, make calls, view logs with contact names and message previews.
- **Email:** Send background emails via SMTP (Gmail supported).
- **Messaging Apps:** WhatsApp and Telegram — opens app with pre-filled message.
- **Contacts:** Full listing with fuzzy name matching for voice commands.
- **System:** Execute shell commands, control brightness, volume, monitor battery.
- **Connectivity:** Toggle WiFi on/off.
- **Media:** Selfie mode (front camera), smart torch with hardware limitation handling.
- **Interactive UI:** `termux-toast` popups and `termux-dialog` prompts.

### Automation & Interfaces
- **Background Daemon:** Clipboard watcher that auto-translates or summarizes copied text.
- **Web Dashboard:** Local browser-based control panel at `http://127.0.0.1:5000`.
- **Telegram Bot:** Remote control from anywhere with authorized chat ID restriction.
- **Enhanced CLI:** Colored output, persistent command history in `~/.andromate/`.

---

## Requirements

> [!WARNING]
> AndroMate only works if the [Termux:API app](https://f-droid.org/packages/com.termux.api/) is installed. Download it from F-Droid before running.

> [!NOTE]
> `ffmpeg` is no longer required. Voice recognition uses native Termux speech-to-text.

> [!WARNING]
> After installing Termux:API, run `termux-speech-to-text` or `termux-sms-send` once manually to grant Android permissions.

---

## Installation

```bash
git clone https://github.com/Anon4You/AndroMate.git
cd AndroMate
bash install.sh
```

The script installs all system and Python dependencies automatically.

After installation, grant required permissions:

```bash
termux-microphone-record    # Voice commands
termux-sms-list             # SMS features
termux-call-log             # Call logs
termux-location             # Location services
```

---

## Usage

| Mode | Command | Description |
|:-----|:--------|:------------|
| **Voice** | `python andromate.py voice` | Native speech-to-text, instant execution |
| **Wake Word** | `python andromate.py wake` | Background listener, activates on trigger phrase |
| **CLI** | `python andromate.py cli` | Interactive shell with coding agent |
| **Web** | `python andromate.py web` | Browser dashboard on port 5000 |
| **Telegram** | `python andromate.py telegram` | Remote control via bot |
| **Daemon** | `python andromate.py` | Background mode, clipboard monitoring |

### CLI Commands

| Command | Description |
|:--------|:------------|
| `/code <task>` | Create or fix code with automatic debugging |
| `/review` | Full project code review with suggestions |
| `/analyze` | Analyze project structure and dependencies |
| `/implement` | Interactive step-by-step implementation |

### Voice Examples

```
"Send an SMS to John saying I'll be late."
"Turn on WiFi."
"Take a selfie."
"Generate an image of a futuristic city."
"Switch to OpenAI provider."
```

---

## Configuration

All settings live in `~/.andromate/config.json`, auto-generated on first run.

```json
{
  "provider": "pollinations",
  "OPENROUTER_API_KEY": "",
  "OPENAI_API_KEY": "",
  "TELEGRAM_BOT_TOKEN": "",
  "TELEGRAM_AUTHORIZED_CHAT_ID": 0,
  "EMAIL_SENDER": "your.email@gmail.com",
  "EMAIL_APP_PASSWORD": "your-16-char-app-password"
}
```

> [!NOTE]
> Pollinations is the default provider. No API key is needed to start immediately.

> [!CAUTION]
> Never use your regular Google password for email. Enable 2FA on your Google account, generate an **App Password** specifically for AndroMate, and use that 16-character password in the config.

### Telegram Setup

1. Create a bot via [@BotFather](https://t.me/BotFather) and copy the token.
2. Get your chat ID by messaging your bot then checking `https://api.telegram.org/bot<TOKEN>/getUpdates`.
3. Add both values to `config.json`.

> [!TIP]
> Keep the Telegram bot or wake word listener running after closing Termux by using `tmux`:
> ```bash
> tmux new -s andromate
> python andromate.py telegram
> # Detach: Ctrl+B, then D
> # Reattach: tmux attach -t andromate
> ```

### Wake Word Customization

Edit the `WAKE_WORDS` list in `modules/wake_word.py`. Fuzzy matching handles slight mispronunciations ("Hey Android" triggers "Hey AndroMate"). The detector pauses during speech output to prevent self-triggering.

---

## Project Structure

```
AndroMate/
├── andromate.py          # Main entry point
└── modules/
    ├── actions.py        # Core actions (Call, SMS, Email, Selfie)
    ├── ai.py             # AI decision routing
    ├── cli.py            # Interactive CLI with coding agent
    ├── clipboard.py      # Clipboard monitoring service
    ├── config.py         # Constants and configuration
    ├── contacts.py       # Fuzzy contact matching
    ├── error_handler.py  # Centralized error logging
    ├── main.py           # Background daemon logic
    ├── notifications.py  # Toast and dialog handlers
    ├── prompt_manager.py # Dynamic AI prompt generation
    ├── providers.py      # API wrappers (OpenRouter, Pollinations, OpenAI)
    ├── shared.py         # Thread-safe flags (speaking state, etc.)
    ├── telegram_bot.py   # Telegram bot interface
    ├── utils.py          # Helpers (TTS, fuzzy matching)
    ├── voice.py          # Native speech-to-text logic
    ├── wake_word.py      # Continuous wake word detector
    └── web_dashboard.py  # Flask web interface
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built for Termux &middot; Powered by AI &middot; Open Source</sub>
</p>
```
