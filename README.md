<p align="center">
  <img src="img/img.png" alt="AndroMate Logo" width="200"/>
  
  <h1 align="center">AndroMate</h1>
  
  <p align="center">
    <strong>A powerful, modular AI assistant for Termux on Android.</strong><br>
    <sub>Control your device with natural language, voice commands, Telegram, or the interactive TUI.</sub>
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
  </p>
</p>

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Provider Management](#provider-management)
- [Telegram Bot](#telegram-bot)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](CONTRIBUTING.md)
- [License](#license)

---

## Features

### Core
- **Multi-Provider AI** — Use any OpenAI-compatible API: OpenAI, OpenRouter, Ollama, LM Studio, vLLM, Groq, Together, and more
- **Unified `/provider` command** — Arrow-key menus with type-to-filter for managing providers (add/edit/remove/switch/test)
- **Rich TUI** — Claude Code-style terminal interface with syntax highlighting, markdown rendering, and prompt bars
- **Native Voice Recognition** — Hands-free control via `termux-speech-to-text`
- **Spoken Feedback** — Uses `termux-tts-speak` for audible confirmations

### Device Control
- **SMS & Calls** — Send SMS, view call logs with contact names, make calls
- **Email** — Send background emails via SMTP (Gmail supported)
- **WhatsApp** — Send messages via `wacli` CLI tool
- **Contacts** — List and search contacts with fuzzy matching
- **System** — Execute shell commands, control brightness, volume, battery
- **Camera** — Take selfies and photos
- **Connectivity** — Toggle WiFi, Bluetooth

### Remote Control
- **Telegram Bot** — Control your device from anywhere via Telegram

---

## Requirements

### System Packages

| Package | Description | Install |
| :--- | :--- | :--- |
| **Termux:API App** | Hardware access bridge | [F-Droid](https://f-droid.org/packages/com.termux.api/) |
| `termux-api` | API interface package | `pkg install termux-api` |
| `wacli` | WhatsApp CLI tool | `pkg install wacli` |

### Python Libraries
```bash
pip install requests rich prompt_toolkit pyfiglet telebot
```

> [!WARNING]
> After installing Termux:API, run commands like `termux-sms-list` and `termux-call-log` once manually to grant Android permissions.

---

## Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/Anon4You/AndroMate.git
   cd AndroMate
   ```

2. **Run the installer**
   ```bash
   bash install.sh
   ```

3. **Grant Termux permissions** (run once)
   ```bash
   termux-microphone-record    # Voice commands
   termux-sms-list             # SMS features
   termux-call-log             # Call logs
   termux-location             # Location services
   ```

4. **Add an AI provider**
   ```bash
   python andromate.py
   /provider                   # Opens the provider manager
   ```
   Any OpenAI-compatible API works. No API key needed for Ollama running locally.

5. **Run**
   ```bash
   python andromate.py         # TUI (default)
   python andromate.py voice   # Voice mode
   python andromate.py telegram # Telegram bot
   ```

---

## Usage

| Mode | Command | Description |
| :--- | :--- | :--- |
| **TUI** | `python andromate.py` | Interactive terminal chat (default) |
| **Voice** | `python andromate.py voice` | Hands-free voice commands |
| **Telegram** | `python andromate.py telegram` | Remote control via Telegram bot |

### Slash Commands

| Command | Description |
| :--- | :--- |
| `/provider` | Manage AI providers (list/add/edit/remove/switch/test) |
| `/settings` | Show current settings |
| `/set-voice` | Toggle voice output on/off |
| `/set-email` | Configure email SMTP |
| `/set-telegram` | Configure Telegram bot |
| `/status` | Show system status |
| `/clear` | Clear conversation history |
| `/help` | Show available commands |

Type `?` for keyboard shortcuts.

### Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| `Up/Down` | Navigate command history |
| `Tab` | Auto-complete commands |
| `Ctrl+C` | Cancel current input |
| `Ctrl+D` | Exit AndroMate |

---

## Provider Management

The `/provider` command opens an arrow-key menu with all provider operations:

- **List** — View all configured providers and which is active
- **Switch Active** — Change the active provider (arrow keys)
- **Add** — Add from presets (OpenRouter, OpenAI, Ollama, LM Studio, Groq, Together, etc.) or custom
- **Edit** — Change model and API key (arrow-key model selection from presets)
- **Remove** — Delete a provider
- **Test** — Verify API connectivity

All selectors support **type-to-filter** — just start typing to narrow down the list.

### Supported Presets

| Provider | Default Model |
| :--- | :--- |
| OpenRouter | `openai/gpt-oss-20b:free` |
| OpenAI | `gpt-4o-mini` |
| Ollama | `llama3` |
| LM Studio | `default` |
| vLLM | `default` |
| Groq | `llama-3.1-8b-instant` |
| Together | `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` |
| Custom | *(your choice)* |

---

## Telegram Bot

Control AndroMate remotely via Telegram:

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your chat ID (message [@userinfobot](https://t.me/userinfobot))
3. Configure in the TUI:
   ```
   /set-telegram
   ```
4. Run: `python andromate.py telegram`

> [!TIP]
> Keep the bot running in the background with `tmux`:
> ```bash
> tmux new -s andromate
> python andromate.py telegram
> # Detach: Ctrl+B, then D
> # Reattach: tmux attach -t andromate
> ```

---

## Configuration

Config is stored at `~/.andromate/config.json` (auto-generated on first run).

### Config Keys

| Key | Default | Description |
| :--- | :--- | :--- |
| `active_provider` | `"openrouter"` | Name of the active provider |
| `providers` | *(list)* | Provider configurations (name, api_key, base_url, model) |
| `enable_voice` | `true` | Enable spoken feedback |
| `email_sender` | `""` | Gmail address for sending emails |
| `email_app_password` | `""` | Gmail app password |
| `telegram_bot_token` | `""` | Telegram bot token |
| `telegram_authorized_chat_id` | `null` | Telegram chat ID for auth |

### Email Setup

```json
{
  "email_sender": "your.email@gmail.com",
  "email_app_password": "your-16-char-app-password"
}
```

> [!CAUTION]
> Never use your regular Google password. Generate an App Password at myaccount.google.com/apppasswords.

---

## Project Structure

```
AndroMate/
├── andromate.py          # Main entry point
└── modules/
    ├── __init__.py
    ├── actions.py        # Device actions (SMS, Call, Email, Camera, Shell)
    ├── ai.py             # AI decision routing
    ├── cli.py            # Rich TUI interface with slash commands
    ├── config.py         # Multi-provider configuration management
    ├── memory.py         # Conversation history (per-provider)
    ├── prompt_manager.py # Dynamic AI prompt generation
    ├── providers.py      # Provider wrappers (OpenAI-compatible)
    ├── telegram_bot.py   # Telegram bot interface
    └── utils.py          # Helpers (TTS, fuzzy matching, contacts)
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE).

---

<p align="center">
  Developed by <a href="https://github.com/Anon4You">Anon4You</a>
</p>
