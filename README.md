# AndroMate 🤖

**AndroMate** is a voice‑controlled AI assistant for Termux on Android. It lets you send messages, make calls, open apps, run shell commands, control device features (torch, brightness, media, etc.), and even chat conversationally – all through natural voice commands.

> ⚠️ **Note:** This tool is still in active development. It works **only inside Termux** on Android devices.

---

## ✨ Features
- 🎤 Voice recognition (Google Speech)
- 🧠 AI decision‑making via OpenRouter (free model)
- 📱 Send SMS, WhatsApp, Telegram, email
- 📞 Make phone calls
- 🚀 Open any app by name
- 🛠️ Execute Termux shell commands
- 🔋 Get battery status, set brightness
- 📸 Take photos, toggle torch
- 🎵 Control media playback
- 📍 Fetch GPS location
- 📋 Monitor and transform clipboard
- 🔔 Auto‑reply to notifications
- 💬 Conversational replies (e.g., “how are you?”)
- 🔊 Spoken confirmations (uses `termux-tts-speak`)


## 📦 Requirements

Make sure the following are installed **inside Termux**:

| Package | Description |
|---------|-------------|
| `termux-api` | Termux:API package (`pkg install termux-api`) |
| **Termux:API app** | Install from F‑Droid (required for hardware access) |
| `ffmpeg` | Audio conversion (`pkg install ffmpeg`) |
| `flac` | Audio codec (`pkg install flac`) |
| `python` | Already included in Termux |
| `requests` | Python HTTP library (`pip install requests`) |
| `SpeechRecognition` | Google speech‑to‑text (`pip install SpeechRecognition`) |

After installing the Termux:API app, run each relevant command once to grant permissions (e.g., `termux-microphone-record`, `termux-sms-send`, etc.).

---

## 🚀 Quick Start
 **Clone the repository** (or copy the files):
   ```bash
git clone https://github.com/Anon4You/AndroMate.git
cd AndroMate
   ```

1. **Set your OpenRouter API key** (free tier available):
```bash
echo "your-api-key-here" > ~/.openrouter_key
```

2. **Run a voice command:**
```bash
python andromate.py voice
```

4. **Run background monitor** (notifications & clipboard):
```bash
python andromate.py
```

---

## 📚 Usage

· python andromate.py voice – greet, listen, and act on one command.
· python andromate.py – background mode (monitors notifications & clipboard).
· Termux widget – place a one‑tap icon on your home screen (see Widget setup).

---

## 🧪 Still in Development

· Some features may be unstable.
· The free AI model can occasionally misinterpret commands.
· Contributions and ideas are welcome!

---

## 📄 License

This project is open‑source. Feel free to modify and share.
