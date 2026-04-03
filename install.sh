#!/data/data/com.termux/files/usr/bin/bash

# AndroMate Installation Script
# This script installs all required dependencies for AndroMate

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║         AndroMate - Installation Script            ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "This script must be run in Termux on Android."
    exit 1
fi

# Update package lists
print_status "Updating package lists..."
pkg update -y

# Install system packages
print_status "Installing system packages..."
pkg install -y python tmux termux-api flac portaudio

# Install tgpt (AI tool)
print_status "Installing tgpt..."
pkg install -y tgpt

# Check if pip is available
if ! command -v pip &> /dev/null; then
    print_error "pip not found. Please ensure Python is properly installed."
    exit 1
fi

# Install Python packages
print_status "Installing Python packages..."
pip install requests SpeechRecognition colorama flask pytelegrambot pyaudio

# Create necessary directories
print_status "Creating configuration directories..."
mkdir -p ~/.andromate

# Create default config if it doesn't exist
if [ ! -f "~/.andromate/config.json" ]; then
    print_status "Creating default configuration..."
    cat > ~/.andromate/config.json << 'EOF'
{
    "AI_PROVIDER": "pollinations",
    "EMAIL_SENDER": "",
    "EMAIL_APP_PASSWORD": "",
    "TELEGRAM_BOT_TOKEN": "",
    "TELEGRAM_AUTHORIZED_CHAT_ID": null,
    "ENABLE_VOICE": true,
    "ENABLE_NOTIFICATIONS": false,
    "ENABLE_CLIPBOARD": false,
    "POLL_INTERVAL": 2,
    "WAKE_WORD_ENABLED": false
}
EOF
    print_success "Default configuration created at ~/.andromate/config.json"
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x *.py 2>/dev/null || true


# Final message
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║          Installation Complete!                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
print_success "AndroMate has been installed successfully!"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit ~/.andromate/config.json to configure your settings"
echo "2. Grant necessary permissions:"
echo "   - termux-microphone-record (for voice commands)"
echo "   - termux-sms-list (for SMS features)"
echo "   - termux-call-log (for call logs)"
echo "   - termux-location (for location services)"
echo "3. Run the assistant:"
echo "   - python andromate.py          (main assistant)"
echo "   - python andromate.py voice    (voice command mode)"
echo "   - python -m modules.cli        (interactive CLI)"
echo "   - python -m modules.web_dashboard  (web interface)"
echo "   - python -m modules.wake_word  (wake word detection)"
echo ""
print_status "For help, check README.md or CONTRIBUTING.md"
echo ""
