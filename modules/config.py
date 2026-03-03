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
    "EMAIL_SENDER": "",
    "EMAIL_APP_PASSWORD": "",
}

# Load user config if exists
_user_config = {}
if os.path.exists(USER_CONFIG_PATH):
    try:
        with open(USER_CONFIG_PATH, "r") as f:
            _user_config = json.load(f)
    except:
        pass

# Apply user overrides (module-level variables)
POLL_INTERVAL = _user_config.get("POLL_INTERVAL", DEFAULTS["POLL_INTERVAL"])
ENABLE_VOICE = _user_config.get("ENABLE_VOICE", DEFAULTS["ENABLE_VOICE"])
ENABLE_NOTIFICATIONS = _user_config.get("ENABLE_NOTIFICATIONS", DEFAULTS["ENABLE_NOTIFICATIONS"])
ENABLE_CLIPBOARD = _user_config.get("ENABLE_CLIPBOARD", DEFAULTS["ENABLE_CLIPBOARD"])
MIN_AI_CALL_INTERVAL = _user_config.get("MIN_AI_CALL_INTERVAL", DEFAULTS["MIN_AI_CALL_INTERVAL"])
AI_PROVIDER = _user_config.get("AI_PROVIDER", DEFAULTS["AI_PROVIDER"])
EMAIL_SENDER = _user_config.get("EMAIL_SENDER", DEFAULTS["EMAIL_SENDER"])
EMAIL_APP_PASSWORD = _user_config.get("EMAIL_APP_PASSWORD", DEFAULTS["EMAIL_APP_PASSWORD"])

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

def reload_config():
    """Reload user configuration from disk and update module-level variables."""
    global POLL_INTERVAL, ENABLE_VOICE, ENABLE_NOTIFICATIONS, ENABLE_CLIPBOARD
    global MIN_AI_CALL_INTERVAL, AI_PROVIDER, EMAIL_SENDER, EMAIL_APP_PASSWORD
    global _user_config

    # Re-read config file
    new_config = {}
    if os.path.exists(USER_CONFIG_PATH):
        try:
            with open(USER_CONFIG_PATH, "r") as f:
                new_config = json.load(f)
        except:
            pass

    _user_config = new_config

    # Update module variables
    POLL_INTERVAL = _user_config.get("POLL_INTERVAL", DEFAULTS["POLL_INTERVAL"])
    ENABLE_VOICE = _user_config.get("ENABLE_VOICE", DEFAULTS["ENABLE_VOICE"])
    ENABLE_NOTIFICATIONS = _user_config.get("ENABLE_NOTIFICATIONS", DEFAULTS["ENABLE_NOTIFICATIONS"])
    ENABLE_CLIPBOARD = _user_config.get("ENABLE_CLIPBOARD", DEFAULTS["ENABLE_CLIPBOARD"])
    MIN_AI_CALL_INTERVAL = _user_config.get("MIN_AI_CALL_INTERVAL", DEFAULTS["MIN_AI_CALL_INTERVAL"])
    AI_PROVIDER = _user_config.get("AI_PROVIDER", DEFAULTS["AI_PROVIDER"])
    EMAIL_SENDER = _user_config.get("EMAIL_SENDER", DEFAULTS["EMAIL_SENDER"])
    EMAIL_APP_PASSWORD = _user_config.get("EMAIL_APP_PASSWORD", DEFAULTS["EMAIL_APP_PASSWORD"])
