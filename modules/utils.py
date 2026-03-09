# modules/utils.py
import re
import time
import subprocess
from difflib import SequenceMatcher
from shared import speaking

def clean_name(name):
    """Remove emojis and non‑printable characters from a name."""
    return re.sub(r'[^\w\s\'-]', '', name).strip()

def fuzzy_match(query, target):
    """Return similarity ratio between two strings."""
    return SequenceMatcher(None, query.lower(), target.lower()).ratio()

class RateLimiter:
    """Simple time‑based rate limiter."""
    def __init__(self, min_interval):
        self.min_interval = min_interval
        self.last_call = 0

    def allow(self):
        now = time.time()
        if now - self.last_call >= self.min_interval:
            self.last_call = now
            return True
        return False

def speak(text):
    """Speak text using termux-tts-speak. Fallback to print if unavailable."""
    try:
        speaking.set(True)
        subprocess.run(["termux-tts-speak", text], check=True, timeout=50)
        # Small delay to let any echo settle before re-enabling listening
        time.sleep(0.5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("")
    finally:
        speaking.set(False)
