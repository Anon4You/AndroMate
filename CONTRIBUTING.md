# 🤝 Contributing to AndroMate

First off, thank you for considering contributing to **AndroMate**! It's people like you that make this tool better for everyone in the Termux community.

## 📖 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Project Structure](#project-structure)

---

## Code of Conduct

This project and everyone participating in it is governed by basic principles of respect and inclusivity. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

---

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as [GitHub Issues](https://github.com/Anon4You/AndroMate/issues). Before creating a bug report, please check existing issues to avoid duplicates.

When creating a bug report, please include as many details as possible:

*   **Device Info:** Android version, Device model.
*   **Termux Version:** Output of `echo $TERMUX_VERSION`.
*   **Command Used:** e.g., `python andromate.py wake` or `python andromate.py telegram`.
*   **Logs:** Paste relevant error output from the terminal.
*   **Steps to Reproduce:** A detailed list of steps to trigger the bug.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub Issues. When suggesting an enhancement:

*   **Use a clear title:** e.g., "Feature: Add support for Bluetooth control".
*   **Describe the solution:** How should it work?
*   **Explain the benefit:** Why would this be useful to other users?

### Pull Requests

1.  **Fork the repo** and create your branch from `main`.
2.  **Make your changes.** Ensure code follows the style guidelines below.
3.  **Test your changes.** Run the specific mode you modified (`voice`, `cli`, `wake`, `web`, `telegram`) to ensure stability.
4.  **Commit your changes.** Use clear commit messages (e.g., `feat: added torch toggle` or `fix: resolved contact name crash`).
5.  **Open a Pull Request.** Reference any relevant issues.

---

## 🛠️ Development Setup

1.  **Clone your fork:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/AndroMate.git
    cd AndroMate
    ```

2.  **Install Dependencies:**
    Ensure you have the prerequisites listed in the [README](README.md#requirements) installed.

> [!NOTE]
> `ffmpeg` is no longer required, but `flac` is necessary for the Wake Word feature.

    ```bash
    pkg install python termux-api tgpt tmux flac
    pip install requests SpeechRecognition colorama flask telebot
    ```

4.  **Configuration (Optional):**
    If you are testing specific features like Email or Telegram, you will need to set up your `~/.andromate/config.json` or API keys as described in the README.

5.  **Testing:**
    There is currently no automated test suite. Testing is done manually by running the assistant in different modes:
    ```bash
    # Test core logic
    python andromate.py cli
    
    # Test web dashboard
    python andromate.py web
    
    # Test wake word (requires flac)
    python andromate.py wake
    ```

---

## 🎨 Style Guidelines

### Python Style
We follow standard **PEP 8** guidelines with a few specifics:

*   **Indentation:** Use 4 spaces, not tabs.
*   **Docstrings:** Use triple quotes (`"""`) for function and module documentation. Explain what the function does, its arguments, and return values.
*   **Imports:** Group imports in the following order: Standard Library, Third Party, Local Application. Separate groups with a blank line.

### Code Structure
Keep the code modular. If you are adding a new capability, follow this guide:

*   **New Device Action (e.g., "Check WiFi status"):**
    1.  Add the logic to `modules/actions.py`.
    2.  Update `modules/config.py` if new constants are needed.
    3.  Update `modules/prompt_manager.py` so the AI knows how to trigger the new action.

*   **New AI Provider:**
    1.  Add the wrapper class/function to `modules/providers.py`.
    2.  Register it in the provider selection logic within `modules/ai.py`.

*   **New Interface (e.g., "Discord Bot"):**
    1.  Create a new file in `modules/` (e.g., `discord_bot.py`).
    2.  Import and initialize it in `andromate.py` under a new argument flag.

### Commit Messages
*   Use the present tense ("Add feature" not "Added feature").
*   Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
*   Limit the first line to 72 characters.

---

## 🧩 Project Structure

Familiarize yourself with the structure before contributing:

```
AndroMate/
├── andromate.py          # Main entry point (CLI args handling)
└── modules/
    ├── __init__.py
    ├── actions.py        # ⭐ Add new device actions here (SMS, Torch, etc.)
    ├── ai.py             # AI decision routing & intent handling
    ├── cli.py            # Interactive CLI loop logic
    ├── clipboard.py      # Clipboard monitoring service
    ├── config.py         # ⭐ Add constants/mappings here
    ├── contacts.py       # Contact name resolution
    ├── error_handler.py  # Centralized error logging
    ├── main.py           # Background daemon logic
    ├── notifications.py  # Toast & Dialog wrappers
    ├── prompt_manager.py # ⭐ Update AI instructions here
    ├── providers.py      # ⭐ Add new AI providers here
    ├── shared.py         # Thread-safe flags (e.g., is_speaking)
    ├── telegram_bot.py   # Telegram bot logic
    ├── utils.py          # Helpers (TTS, fuzzy matching)
    ├── voice.py          # Native Termux speech-to-text
    ├── wake_word.py      # Continuous wake word listener
    └── web_dashboard.py  # Flask web server
```

> [!TIP]
> If you are unsure where a change belongs, open an issue and ask! We are happy to help guide you.

---

Thank you for your contribution! 🚀
