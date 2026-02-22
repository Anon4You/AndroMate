# clipboard.py
import subprocess
from ai import ask_ai
from config import MIN_AI_CALL_INTERVAL
from utils import RateLimiter

clip_limiter = RateLimiter(MIN_AI_CALL_INTERVAL)

def get_clipboard():
    """Fetch clipboard content; always return a string."""
    try:
        result = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""

def transform_text(text, operation):
    operation = operation.lower()
    if "summarize" in operation:
        return text[:100] + ("..." if len(text) > 100 else "")
    elif "translate" in operation:
        return f"[Translated from '{operation}']: {text}"
    else:
        return text

def monitor_clipboard(last_text):
    current = get_clipboard()
    if current and current != last_text and len(current) > 10:
        print(f"Clipboard changed: {current[:50]}...")
        if clip_limiter.allow():
            decision = ask_ai(current, context="clipboard")
            if decision.get('action') == 'clipboard_action':
                transform = decision.get('transform', '')
                transformed = transform_text(current, transform)
                if transformed != current:
                    subprocess.run(["termux-clipboard-set", transformed])
                    subprocess.run([
                        "termux-notification",
                        "--id", "clipboard",
                        "--title", "Clipboard transformed",
                        "--content", transformed
                    ])
                    print(f"Transformed clipboard to: {transformed}")
                    return transformed
        else:
            print("Rate limited: skipping AI processing for clipboard change.")
    return current or last_text
