# error_handler.py
import os
import sys
import traceback
from datetime import datetime
from utils import speak

LOG_FILE = os.path.expanduser("~/andromate_errors.log")

def log_error(error, context="", notify_user=True):
    """Log an error to file, optionally speak and notify."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{timestamp}] {context}: {error}\n{traceback.format_exc()}"
    # Write to log file
    try:
        with open(LOG_FILE, "a") as f:
            f.write(error_msg + "\n")
    except:
        pass
    # Print to terminal
    print(error_msg, file=sys.stderr)
    # Speak a friendly message (if desired)
    if notify_user:
        speak("Sorry, I encountered an error. Check the log for details.")
    # Optionally show a Termux notification
    try:
        subprocess.run(["termux-notification", "--id", "andromate_error",
                        "--title", "AndroMate Error",
                        "--content", str(error)[:100]], timeout=2)
    except:
        pass
