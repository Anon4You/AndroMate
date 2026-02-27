<p align="center">
  <h1 align="center">AndroMate 🤖</h1>
  <p align="center">
    <em>A powerful, voice-controlled AI assistant designed specifically for Termux on Android.</em>
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#prerequisites">Prerequisites</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#license">License</a>
  </p>
</p>

---

## 📝 Overview

**AndroMate** bridges the gap between natural language processing and Android system controls. By leveraging the Termux API and OpenRouter's AI capabilities, AndroMate allows users to interact with their device using natural voice commands or a CLI interface.

Whether you need to send messages, toggle hardware settings, execute shell scripts, or simply chat, AndroMate acts as a unified interface for device automation.

> ⚠️ **Status:** This project is in active development. It is designed exclusively for the Termux environment on Android.

---

## ✨ Key Features

### 🧠 AI & Interaction
*   **Natural Language Processing:** Powered by OpenRouter (supports free models) to understand intent.
*   **Voice Recognition:** Utilizes Google Speech-to-Text for hands-free command execution.
*   **Conversational Mode:** Engages in dialogue and answers general queries.
*   **Audible Feedback:** Provides spoken confirmations via `termux-tts-speak`.

### 📱 Device Control
*   **Communication:** Send SMS, WhatsApp, Telegram, and Email messages; make phone calls.
*   **System Automation:** Open apps by name, execute shell commands, and manage clipboard content.
*   **Hardware Access:** Get battery status, set screen brightness, take photos, and toggle the torch.
*   **Media & Location:** Control media playback and fetch current GPS coordinates.
*   **Background Monitoring:** Auto-reply to notifications and monitor clipboard changes.

---

## 📦 Prerequisites

To ensure full functionality, the following components must be installed and configured in your Termux environment.

### System Dependencies
Ensure you have the **Termux:API** app installed from F-Droid (essential for hardware access).

```bash
pkg update && pkg upgrade
pkg install termux-api ffmpeg flac python
```

### Python Libraries
Install the required Python packages:

```bash
pip install requests SpeechRecognition
```

> **Note:** After installing the Termux:API app, manually run commands like `termux-microphone-record` or `termux-sms-send` once to grant the necessary Android permissions.

---

## 🚀 Installation

Follow these steps to get AndroMate up and running.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Anon4You/AndroMate.git
    cd AndroMate
    ```

2.  **Configure API Key**
    AndroMate requires an OpenRouter API key for AI decision-making. You can obtain a free key from [OpenRouter](https://openrouter.ai/).
    
    Save your key to the configuration file:
    ```bash
    echo "YOUR_OPENROUTER_API_KEY" > ~/.openrouter_key
    ```

---

## 💻 Usage

AndroMate offers three distinct modes of operation:

### 1. Voice Mode (Interactive)
Activate the assistant to listen for a single command.
```bash
python andromate.py voice
```

### 2. CLI Mode (Interactive Shell)
Type commands directly into an interactive prompt.
```bash
python andromate.py cli
```

### 3. Background Mode (Daemon)
Runs silently to monitor notifications and clipboard activity.
```bash
python andromate.py
```

### 📱 Widget Integration
For quick access, you can create a Termux widget shortcut on your home screen. Refer to the [Termux:Widget](https://wiki.termux.com/wiki/Termux:Widget) documentation for setup instructions.

---

## 🛠️ Development Status

AndroMate is currently in **Beta**.

*   **Stability:** Some features may be subject to instability depending on device Android version.
*   **AI Accuracy:** The default free AI model may occasionally misinterpret complex commands.
*   **Contributing:** We welcome contributions, bug reports, and feature requests. Please feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is open-sourced under the MIT License. You are free to modify, distribute, and use the code for personal or commercial purposes.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/Anon4You">Anon4You</a>
</p>
