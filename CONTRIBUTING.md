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
*   **Command Used:** e.g., `python andromate.py voice`.
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
3.  **Test your changes.** Run the specific mode you modified (`voice`, `cli`, or background) to ensure stability.
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
    ```bash
    pkg install python termux-api ffmpeg flac
    pip install requests SpeechRecognition
    ```

3.  **Testing:**
    There is currently no automated test suite. Testing is done manually by running the assistant:
    ```bash
    python andromate.py cli
    ```

---

## 🎨 Style Guidelines

### Python Style
We follow standard **PEP 8** guidelines with a few specifics:

*   **Indentation:** Use 4 spaces, not tabs.
*   **Docstrings:** Use triple quotes (`"""`) for function and module documentation. Explain what the function does, its arguments, and return values.
*   **Imports:** Group imports in the following order: Standard Library, Third Party, Local Application. Separate groups with a blank line.

### Code Structure
Keep the code modular. If you are adding a new device capability (e.g., "Check WiFi status"):
1.  Add the logic to `modules/actions.py` or create a new module if the feature is complex.
2.  Update `modules/config.py` if new constants or mappings are needed.
3.  Update `prompt_manager.py` if the AI needs new instructions to understand the command.

### Commit Messages
*   Use the present tense ("Add feature" not "Added feature").
*   Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
*   Limit the first line to 72 characters.

---

## 🧩 Project Structure

Familiarize yourself with the structure before contributing:

```
AndroMate/
├── andromate.py         # Entry point
└── modules/
    ├── actions.py       # ⭐ Add new device actions here
    ├── ai.py            # AI logic and decision handling
    ├── config.py        # ⭐ Add constants/config here
    ├── providers.py     # ⭐ Add new AI providers here
    ├── utils.py         # Helper functions (TTS, etc.)
    └── ...              # Other utility modules
```

---

Thank you for your contribution! 🚀
