# config.py
import os

# Poll interval (seconds)
POLL_INTERVAL = 2

# Feature toggles (set False to disable)
ENABLE_VOICE = True
ENABLE_NOTIFICATIONS = True
ENABLE_CLIPBOARD = True

# Rate limiting for AI calls (seconds between calls)
MIN_AI_CALL_INTERVAL = 5

# OpenRouter – try environment variable, then file
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    try:
        key_file = os.path.expanduser("~/.openrouter_key")
        with open(key_file, "r") as f:
            OPENROUTER_API_KEY = f.read().strip()
    except:
        OPENROUTER_API_KEY = None
        print("Warning: OPENROUTER_API_KEY not set and ~/.openrouter_key not found.")

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
