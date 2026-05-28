# modules/config.py
import os
import json

USER_CONFIG_PATH = os.path.expanduser("~/.andromate/config.json")

# Default settings
DEFAULTS = {
    "enable_voice": True,
    "email_sender": "",
    "email_app_password": "",
    "telegram_bot_token": "",
    "telegram_authorized_chat_id": None,
}

# Default providers to create if none exist
DEFAULT_PROVIDERS = [
    {
        "name": "opengateway",
        "api_key": "",
        "base_url": "https://opengateway.gitlawb.com/v1",
        "model": "mimo-v2.5-pro",
    },
    {
        "name": "openrouter",
        "api_key": "",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-oss-20b:free",
    },
    {
        "name": "ollama",
        "api_key": "ollama",
        "base_url": "http://localhost:11434/v1",
        "model": "llama3",
    },
]
DEFAULT_ACTIVE_PROVIDER = "openrouter"

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


def _load_config():
    """Load user config from disk."""
    if os.path.exists(USER_CONFIG_PATH):
        try:
            with open(USER_CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_config(data):
    """Save config to disk."""
    os.makedirs(os.path.dirname(USER_CONFIG_PATH), exist_ok=True)
    with open(USER_CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


def _migrate_old_config(cfg):
    """Migrate old flat config format to new multi-provider format."""
    changed = False
    if "OPENGATEWAY_API_KEY" in cfg:
        old_key = cfg.pop("OPENGATEWAY_API_KEY", "")
        old_base = cfg.pop("OPENGATEWAY_BASE", "https://opengateway.gitlawb.com/v1")
        old_model = cfg.pop("OPENGATEWAY_MODEL", "mimo-v2.5-pro")
        cfg.pop("AI_PROVIDER", None)
        cfg.pop("POLL_INTERVAL", None)
        cfg.pop("MIN_AI_CALL_INTERVAL", None)
        cfg.pop("ENABLE_NOTIFICATIONS", None)
        cfg.pop("ENABLE_CLIPBOARD", None)
        cfg.pop("WAKE_WORD_ENABLED", None)
        if "ENABLE_VOICE" in cfg:
            cfg["enable_voice"] = cfg.pop("ENABLE_VOICE")
        cfg["providers"] = [{
            "name": "opengateway",
            "api_key": old_key,
            "base_url": old_base,
            "model": old_model,
            "headers": {},
        }]
        cfg["active_provider"] = "opengateway"
        changed = True
    return cfg, changed


# Load on import
_user_config = _load_config()
_user_config, _migrated = _migrate_old_config(_user_config)

# If no providers, create defaults
if not _user_config.get("providers"):
    _user_config["providers"] = DEFAULT_PROVIDERS.copy()
    _user_config["active_provider"] = DEFAULT_ACTIVE_PROVIDER
    _migrated = True

if _migrated:
    _save_config(_user_config)

# Module-level flat settings
ENABLE_VOICE = _user_config.get("enable_voice", DEFAULTS["enable_voice"])
EMAIL_SENDER = _user_config.get("email_sender", DEFAULTS["email_sender"])
EMAIL_APP_PASSWORD = _user_config.get("email_app_password", DEFAULTS["email_app_password"])
TELEGRAM_BOT_TOKEN = _user_config.get("telegram_bot_token", DEFAULTS["telegram_bot_token"])
TELEGRAM_AUTHORIZED_CHAT_ID = _user_config.get("telegram_authorized_chat_id", DEFAULTS["telegram_authorized_chat_id"])


# ── Provider Management ──────────────────────────────────────────────

def get_providers():
    """Return list of all configured providers."""
    cfg = _load_config()
    return cfg.get("providers", [])


def get_active_provider():
    """Return the active provider dict, or None if not configured."""
    cfg = _load_config()
    providers = cfg.get("providers", [])
    active_name = cfg.get("active_provider", "")
    for p in providers:
        if p.get("name") == active_name:
            return p
    if providers:
        return providers[0]
    return None


def get_active_provider_name():
    """Return the active provider name string."""
    cfg = _load_config()
    return cfg.get("active_provider", "")


def save_providers(providers, active_name=None):
    """Save providers list and optionally the active provider name."""
    cfg = _load_config()
    cfg["providers"] = providers
    if active_name is not None:
        cfg["active_provider"] = active_name
    elif not cfg.get("active_provider") and providers:
        cfg["active_provider"] = providers[0]["name"]
    _save_config(cfg)


def add_provider(name, api_key, base_url, model, headers=None):
    """Add a new provider. Returns True on success, False if name exists."""
    cfg = _load_config()
    providers = cfg.get("providers", [])
    for p in providers:
        if p["name"] == name:
            return False
    providers.append({
        "name": name,
        "api_key": api_key,
        "base_url": base_url.rstrip("/"),
        "model": model,
        "headers": headers or {},
    })
    cfg["providers"] = providers
    if not cfg.get("active_provider"):
        cfg["active_provider"] = name
    _save_config(cfg)
    return True


def update_provider(name, api_key=None, base_url=None, model=None, headers=None):
    """Update an existing provider's fields. Returns True on success."""
    cfg = _load_config()
    providers = cfg.get("providers", [])
    for p in providers:
        if p["name"] == name:
            if api_key is not None:
                p["api_key"] = api_key
            if base_url is not None:
                p["base_url"] = base_url.rstrip("/")
            if model is not None:
                p["model"] = model
            if headers is not None:
                p["headers"] = headers
            cfg["providers"] = providers
            _save_config(cfg)
            return True
    return False


def edit_provider(name, **kwargs):
    """Edit an existing provider's fields. Returns True on success."""
    cfg = _load_config()
    providers = cfg.get("providers", [])
    for p in providers:
        if p["name"] == name:
            for key in ("api_key", "base_url", "model", "headers"):
                if key in kwargs:
                    p[key] = kwargs[key]
            if "new_name" in kwargs and kwargs["new_name"] != name:
                old_name = name
                p["name"] = kwargs["new_name"]
                if cfg.get("active_provider") == old_name:
                    cfg["active_provider"] = kwargs["new_name"]
            cfg["providers"] = providers
            _save_config(cfg)
            return True
    return False


def remove_provider(name):
    """Remove a provider by name. Returns True on success."""
    cfg = _load_config()
    providers = cfg.get("providers", [])
    new_providers = [p for p in providers if p["name"] != name]
    if len(new_providers) == len(providers):
        return False
    cfg["providers"] = new_providers
    if cfg.get("active_provider") == name:
        cfg["active_provider"] = new_providers[0]["name"] if new_providers else ""
    _save_config(cfg)
    return True


def set_active_provider(name):
    """Set the active provider by name. Returns True on success."""
    cfg = _load_config()
    providers = cfg.get("providers", [])
    for p in providers:
        if p["name"] == name:
            cfg["active_provider"] = name
            _save_config(cfg)
            return True
    return False


def get_setting(key, default=None):
    """Get a flat config setting."""
    cfg = _load_config()
    return cfg.get(key, default)


def set_setting(key, value):
    """Set a flat config setting and save."""
    cfg = _load_config()
    cfg[key] = value
    _save_config(cfg)


def reload_config():
    """Reload user configuration from disk and update module-level variables."""
    global ENABLE_VOICE, EMAIL_SENDER, EMAIL_APP_PASSWORD
    global TELEGRAM_BOT_TOKEN, TELEGRAM_AUTHORIZED_CHAT_ID

    new_config = _load_config()

    ENABLE_VOICE = new_config.get("enable_voice", DEFAULTS["enable_voice"])
    EMAIL_SENDER = new_config.get("email_sender", DEFAULTS["email_sender"])
    EMAIL_APP_PASSWORD = new_config.get("email_app_password", DEFAULTS["email_app_password"])
    TELEGRAM_BOT_TOKEN = new_config.get("telegram_bot_token", DEFAULTS["telegram_bot_token"])
    TELEGRAM_AUTHORIZED_CHAT_ID = new_config.get("telegram_authorized_chat_id", DEFAULTS["telegram_authorized_chat_id"])
