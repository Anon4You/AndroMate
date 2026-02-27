# config.py
import os
import json

USER_CONFIG_PATH = os.path.expanduser("~/.andromate/config.json")

# Default settings
DEFAULTS = {
    "POLL_INTERVAL": 2,
    "ENABLE_VOICE": True,
    "ENABLE_NOTIFICATIONS": True,
    "ENABLE_CLIPBOARD": True,
    "MIN_AI_CALL_INTERVAL": 5,
    "AI_PROVIDER": "pollinations",  # default
}

# Load user config if exists
user_config = {}
if os.path.exists(USER_CONFIG_PATH):
    try:
        with open(USER_CONFIG_PATH, "r") as f:
            user_config = json.load(f)
    except:
        pass

# Apply user overrides
POLL_INTERVAL = user_config.get("POLL_INTERVAL", DEFAULTS["POLL_INTERVAL"])
ENABLE_VOICE = user_config.get("ENABLE_VOICE", DEFAULTS["ENABLE_VOICE"])
ENABLE_NOTIFICATIONS = user_config.get("ENABLE_NOTIFICATIONS", DEFAULTS["ENABLE_NOTIFICATIONS"])
ENABLE_CLIPBOARD = user_config.get("ENABLE_CLIPBOARD", DEFAULTS["ENABLE_CLIPBOARD"])
MIN_AI_CALL_INTERVAL = user_config.get("MIN_AI_CALL_INTERVAL", DEFAULTS["MIN_AI_CALL_INTERVAL"])
AI_PROVIDER = user_config.get("AI_PROVIDER", DEFAULTS["AI_PROVIDER"])

# OpenRouter – try environment variable, then file
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    try:
        with open(os.path.expanduser("~/.openrouter_key")) as f:
            OPENROUTER_API_KEY = f.read().strip()
    except:
        OPENROUTER_API_KEY = None
        # Don't warn here; will be handled when actually used

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Map common app names to actual Android package names
APP_NAME_TO_PACKAGE = {
    "whatsapp": "com.whatsapp",
    "youtube": "com.google.android.youtube",
    "spotify": "com.spotify.music",
    "chrome": "com.android.chrome",
    "gmail": "com.google.android.gm",
    "messages": "com.google.android.apps.messaging",
    "phone": "com.google.android.dialer",
    "camera": "com.android.camera",
    "settings": "com.android.settings",
    "play store": "com.android.vending",
    "maps": "com.google.android.apps.maps",
    "telegram": "org.telegram.messenger",
    "twitter": "com.twitter.android",
    "instagram": "com.instagram.android",
    "facebook": "com.facebook.katana",
}
