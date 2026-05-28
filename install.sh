#!/data/data/com.termux/files/usr/bin/bash

# AndroMate v2.0 Installation Script

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║         AndroMate v2.0 — Install Script           ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status()  { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# Check Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "This script must be run in Termux on Android."
    exit 1
fi

# Update packages
print_status "Updating package lists..."
apt update -y

# Install system packages
print_status "Installing system packages..."
apt install -y python tmux termux-api flac portaudio tgpt wacli

# Install Python packages
print_status "Installing Python packages..."
pip install requests rich prompt_toolkit pyfiglet telebot SpeechRecognition colorama flask pyaudio

# Create config directory
mkdir -p ~/.andromate

# Write default config (only if it doesn't exist)
if [ ! -f ~/.andromate/config.json ]; then
    print_status "Writing default configuration..."
    cat > ~/.andromate/config.json << 'EOF'
{
    "active_provider": "openrouter",
    "providers": [
        {
            "name": "opengateway",
            "api_key": "",
            "base_url": "https://opengateway.gitlawb.com/v1",
            "model": "mimo-v2.5-pro"
        },
        {
            "name": "openrouter",
            "api_key": "",
            "base_url": "https://openrouter.ai/api/v1",
            "model": "openai/gpt-oss-20b:free"
        },
        {
            "name": "ollama",
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1",
            "model": "llama3"
        }
    ],
    "enable_voice": true,
    "email_sender": "",
    "email_app_password": "",
    "telegram_bot_token": "",
    "telegram_authorized_chat_id": null
}
EOF
    print_success "Config written to ~/.andromate/config.json"
else
    print_status "Config already exists, skipping."
fi

# Done
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║          Installation Complete!                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo ""
echo "  1. Run AndroMate:"
echo "     python andromate.py            TUI (default)"
echo "     python andromate.py voice      Voice mode"
echo "     python andromate.py telegram   Telegram bot"
echo ""
echo "  2. Add an AI provider:"
echo "     /provider                      Arrow-key provider manager"
echo ""
echo "  3. Grant Termux permissions (run once):"
echo "     termux-microphone-record       Voice commands"
echo "     termux-sms-list                SMS features"
echo "     termux-call-log                Call logs"
echo ""
echo -e "  Docs: ${BLUE}README.md${NC} | ${BLUE}CONTRIBUTING.md${NC}"
echo ""
