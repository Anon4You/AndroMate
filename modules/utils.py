# utils.py
import re
import time
import subprocess
from difflib import SequenceMatcher
from shared import speaking


def _is_voice_enabled():
    """Check if voice output should be used (avoid circular import)."""
    try:
        from actions import is_voice_enabled
        return is_voice_enabled()
    except ImportError:
        return True


def clean_name(name):
    """Remove emojis and non-printable characters from a name."""
    return re.sub(r'[^\w\s\'-]', '', name).strip()


def fuzzy_match(query, target):
    """Return similarity ratio between two strings."""
    return SequenceMatcher(None, query.lower(), target.lower()).ratio()


def speak(text):
    """Speak text using termux-tts-speak. Respects voice-enabled flag."""
    if not _is_voice_enabled():
        return

    try:
        speaking.set(True)
        subprocess.run(["termux-tts-speak", text], check=True, timeout=50)
        time.sleep(0.5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    finally:
        speaking.set(False)
