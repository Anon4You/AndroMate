# notifications.py
import json
import subprocess
from ai import ask_ai
from actions import execute_action
from config import MIN_AI_CALL_INTERVAL
from utils import RateLimiter

notif_limiter = RateLimiter(MIN_AI_CALL_INTERVAL)

def get_notifications():
    """Fetch notifications; always return a list."""
    try:
        result = subprocess.run(["termux-notification-list"], capture_output=True, text=True, check=True)
        if result.stdout:
            return json.loads(result.stdout)
        else:
            return []
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return []

def monitor_notifications(previous_ids):
    current = get_notifications()
    # Ensure current is a list (should be, but just in case)
    if not isinstance(current, list):
        current = []
    new = [n for n in current if n.get('id') not in previous_ids]
    for notif in new:
        title = notif.get('title', '')
        content = notif.get('content', '')
        package = notif.get('packageName', 'unknown')
        full_text = f"{title} {content}".strip()
        if full_text:
            print(f"New notification from {package}: {full_text}")
            if notif_limiter.allow():
                decision = ask_ai(full_text, context="notification")
                if decision.get('action') == 'reply_notification':
                    decision['app'] = package
                execute_action(decision)
            else:
                print("Rate limited: skipping AI processing for this notification.")
    return [n.get('id') for n in current]
